#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler
from logging import Formatter, DEBUG
from datetime import timedelta, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from os import path, remove
from smtplib import SMTP
from re import sub, search
import traceback
import json

from flask import Flask, render_template, redirect, request, session, url_for
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from PIL import Image
import simplepam
import difflib

from Postgres import PersonelModel, DatathonModel
from config import SERVICE_ACCOUNT_EMAIL, SERVICE_ACCOUNT_KEY, GCP_SECRET_KEY

app = Flask(__name__)

app.config.update(
        PERMANENT_SESSION_LIFETIME=timedelta(seconds=3000),
        SECRET_KEY='mf}7WwDxTm8ik}ipULrYgSWzfxutj|zDo1n(h+abvE&$aM)?O$8R>qUtE)?CyOQ)*6YwADN!IHLy+TE^K1>>1^riVxme**JBH!+N',
        MAX_CONTENT_PATH=5 * 1024 * 1024,
        TEMPLATES_AUTO_RELOAD=True,
        UPLOAD_FOLDER="static/images/"
        )

# Set logging information
LOG_HANDLER = RotatingFileHandler('/var/log/flask/lcp_website.log',
                                  maxBytes=10000000, backupCount=2)
LOG_HANDLER.setLevel(DEBUG)
LOG_HANDLER.setFormatter(
    Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(message)s"))
app.logger.addHandler(LOG_HANDLER)
app.logger.setLevel(DEBUG)

ADMIN = ["ftorres", "rgmark", "kpierce", "alistairewj", "tpollard"]
EMAIL_RECIPIENTS = ['ftorres@mit.edu', 'kpierce@mit.edu']
PRIMARY_ADMIN = ['ftorres@mit.edu']

GCP_DELEGATION_EMAIL = 'ftorres@physionet.org'
DATATHON_GROUP = "datathon@physionet.org"


def login_required(function):
    """
    Wrapper function to force login
    """
    @wraps(function)
    def wrap(*args, **kwargs):
        # if user is not logged in, redirect to login page
        if ('Username' not in session) or ('URL' not in session):
            return redirect(url_for('login'))
        return function(*args, **kwargs)
    return wrap


@app.errorhandler(404)
def page_not_found(error):
    """
    Convert 404 page to a custom template.
    """
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(error):
    """
    This is the page for handling internal server error
    there will be a log in apache and email generated
    """
    trace = traceback.format_exc()
    location = request.path
    app.logger.error("500 - Internal Server Error - {0}\n{1}\n".format(
        location, trace))

    content = "There was a internal server error on the Flask app running the \
    LCP website. \nThe time of this error is: {0}\nError traceback:\n{2}\
    ".format(datetime.now(), trace)
    if 'Username' in session:
        content += "\nThe user tha triggered this error is: {0}".format(
            session['Username'])
    send_email("Internal Server Error - Flask LCP - {0}".format(location),
               content, 'noreply_error@lcp.mit.edu')
    return render_template('500.html')


@app.route('/robots.txt')
def send_text_file():
    """
    Serve robots file
    """
    return app.send_static_file('robots.txt')


def send_email(subject, content, sender, rec=None):
    """
    Send plain text email
    """
    server = SMTP('127.0.0.1')
    msg = MIMEText(content, 'plain')
    recipients = PRIMARY_ADMIN
    if rec is not None:
        recipients = rec
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()


def send_html_email(subject, content, html_content, sender, rec=None):
    """
    This functions sends an email, takes subject, content, sender and recipient
    The recipients has to be a list of emails, even is there is only one

    Here a HTML email will be sent.

    ONLY used in BIO edits.
    """
    msg = MIMEMultipart('alternative')
    recipients = PRIMARY_ADMIN
    if rec is not None:
        recipients = rec
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    html = """\
    <html>
      <head></head>
      <body>
        {0}
      </body>
    </html>
    """.format(html_content)
    part1 = MIMEText(content, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    server = SMTP('127.0.0.1')
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()


def checkout_form(var):
    """
    Checkout form that will be called in the submittion of the 'info/submit'
    """
    subject = 'LCP checkout form - {0}'.format(var['email'])
    content = "\nLastname: {0}\nFirstname: {1}\nEnd date: {2}\n\
    Archive location:\nMachine name: {3}\nFilepath: {4}\n\
    Special instructions: {5}\nNew preferred e-mail address: {6}\n\
    Valid from (date): {7}\nNew office address: {8}\nValid from (date): {9}\n\
    New home address: {10}\nNew telephone number(s): {11}\n\
    Anything else: {12}\n".format(
        var['lastname'], var['firstname'], var['enddate'], var['machine'],
        var['filepath'], var['instructions'], var['email'], var['email-when'],
        var['office-address'], var['office-when'], var['home-address'],
        var['phone'], var['extra'])

    # Log the variables in case an error occurs.
    app.logger.info("A person did the checkout form. Variables are the \
        following: {}".format(var))

    # Insert the checkout form into the database
    model = PersonelModel()
    result = model.checkout_form(var)

    send_email(subject=subject, content=content, sender=var['email'],
               rec=EMAIL_RECIPIENTS)

    if result is not True:
        app.logger.error("There was an error in the postgres insert of the \
                         checkout_form\n{0}\n{1}".format(content, result))
        send_email("There was an error in the Checkout form line insert",
                   result, 'noreply@lcp.mit.edu')
        return result
    return content


def registration_form(var):
    '''
    Check in form that will be called in the submittion of the 'info/submit'
    '''
    picture = 'missing.jpg'

    if request.files.get("picture"):
        app.logger.info("Image found in the registration form.")
        if var["y"] and var["x"] and var["height"] and var["width"]:
            picture = resize_image()
        else:
            app.logger.error("ERROR, missing axis in the image")
            session['ERROR'] = "Error uploading the image."
            picture = 'missing.jpg'

    subject = 'LCP registration form - {0}'.format(var['email'])

    content = "\nFull Name: {0} {1}\n\nStart date: {2}\nMIT username: {3}\
    \nLCP username: {4}\nMIT ID number: {5}\nPreferred e-mail address: {6}\
    \nOffice address: {7}\nHome address: {8}\nTelephone number(s): {9}\
    \nEmergency contact: {10}\nCurrent project(s) in LCP: {11} \
    \nFocus of research: {12}\nBio: {13}\nPicture: {14}\
    \nEHS training date: {15}\nHuman studies training date: {16}\
    \nAnything else: {17}\n".format(
        var['firstname'], var['lastname'], var['startdate'], var['username'],
        var['lcp_username'], var['id'], var['email'], var['office-address'],
        var['home-address'], var['phone'], var['emergency-contact'],
        var['research'], var['Other'], var['Bio'], picture,
        var['ehs_training'], var['extra'], var['human_studies_training'])

    app.logger.info("Checking form submitted:\n{}\n".format(var))
    result = PersonelModel().registration_form(var, picture)
    # Alert that the users have been submitted
    send_email(subject=subject, content=content, sender=var['email'],
               rec=EMAIL_RECIPIENTS)

    if result is not True:
        app.logger.error("There was an error in the postgres insert of the \
                         Registration_form\n{0}\n{1}".format(content, result))
        send_email("There was an error in the Checkin form line insert",
                   result, 'noreply@lcp.mit.edu')
        return result
    return content


def resize_image():
    """
    Function that takes a image to crop and upload ßit.
    """
    x_axis = float(request.form.get('x', None))
    y_axis = float(request.form.get('y', None))
    width = float(request.form.get('width', None))
    height = float(request.form.get('height', None))
    file = request.files['picture']
    uid = request.form.get('UID', None)
    username = ''
    if uid is not None:
        username = PersonelModel().get_username_from_id(uid)
    else:
        username = request.form.get('email', None).split("@")[0]

    filename = username + '.' + file.filename.split('.')[-1]
    if path.exists(app.config['UPLOAD_FOLDER'] + filename):
        remove(app.config['UPLOAD_FOLDER'] + filename)

    image = Image.open(file)
    image = image.crop((x_axis, y_axis, width+x_axis, height+y_axis))
    image = image.resize((200, 200), Image.ANTIALIAS)
    image.save(app.config['UPLOAD_FOLDER'] + filename)
    return filename


def auth(username, passwd):
    """
    Authentication function against the system users.
    """
    result = simplepam.authenticate(str(username), str(passwd))
    # Personel = PersonelModel()
    if result:
        session["Username"] = username
        session['URL'] = "https://lcp.mit.edu"
        return True
    app.logger.error('Incorrect password or username: {0} Error: {1}'.format(
        username, result))
    return False


def show_diff(text, n_text):
    """
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output = []
    for opcode, a_0, a_1, b_0, b_1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a_0:a_1])
        elif opcode == 'insert':
            output.append("<font color=red>^{0}</font>".format(
                seqm.b[b_0:b_1]))
        elif opcode == 'delete':
            output.append("<font color=blue>^{0}</font>".format(
                seqm.a[a_0:a_1]))
        elif opcode == 'replace':
            output.append("<font color=green>^{0}</font>".format(
                seqm.b[b_0:b_1]))
        else:
            raise Exception("unexpected opcode")
    return ''.join(output)

###############################################################################
#
# Pages for the LCP registration, checkout and basic information for the lab.
#
###############################################################################
@app.route("/info/")
@app.route("/info/index")
@app.route("/info/index.html")
def lab_index():
    """
    Index page for the lab info
    """
    return render_template('info/index.html')


@app.route("/info/reg_form")
@app.route("/info/reg_form.html")
def reg_form():
    """
    Registration form for new lab members
    """
    return render_template('info/registration_form.html')


@app.route("/info/intro_to_Mark_lab")
@app.route("/info/intro_to_Mark_lab.html")
def lcp_intro():
    """
    Basic lab info
    """
    return render_template('info/intro_to_Mark_lab.html')


@app.route("/info/check_out_form")
@app.route("/info/check_out_form.html")
def check_out_form():
    """
    Form for when a person leaves
    """
    return render_template('info/check_out_form.html')


@app.route("/info/submit", methods=['POST'])
def submit():
    """
    This form accept both registration and checkout form.
    """
    app.logger.info("Person doing the registration\n")
    app.logger.info(request.form)
    var = {'firstname': request.form.get('firstname', None),
           'lastname': request.form.get('lastname', None),
           'startdate': request.form.get('startdate', None),
           'username': request.form.get('username', None),
           'lcp_username': request.form.get('lcp_username', None),
           'id': request.form.get('id', None),
           'email': request.form.get('email', None),
           'office-address': request.form.get('office-address', None),
           'home-address': request.form.get('home-address', None),
           'phone': request.form.get('phone', None),
           'emergency-contact': request.form.get('emergency-contact', None),
           'research': request.form.get('research', None),
           'Other': request.form.get('Other', None),
           'Bio': request.form.get('Bio', None),
           'ehs_training': request.form.get('ehs_training', None),
           'human_studies_training': request.form.get('human_studies_training',
                                                      None),
           'extra': request.form.get('extra', None),
           'enddate': request.form.get('enddate', None),
           'machine': request.form.get('machine', None),
           'filepath': request.form.get('filepath', None),
           'instructions': request.form.get('instructions', None),
           'email-when': request.form.get('email-when', None),
           'office-when': request.form.get('office-when', None),
           'y': request.form.get("y", None), 'x': request.form.get("x", None),
           'height': request.form.get("height", None),
           'width': request.form.get("width", None)}

    content = ''
    if request.form.get('Registration_form', 'None') != 'None':
        content = registration_form(var)
    elif request.form.get('Checkout_form', 'None') != 'None':
        content = checkout_form(var)
    else:
        return render_template('info/index.html')
    return render_template('info/submit.html',
                           Content=content.replace("\n", "<br>"))

###############################################################################
#
# Main pages for the LCP website
#
###############################################################################
@app.route("/")
@app.route("/index")
@app.route("/index.html")
@app.route("/index.shtml")
def index():
    """
    LCP index page
    """
    return render_template('index.html')


@app.route("/publications")
@app.route("/Publications")
@app.route("/publications.html")
@app.route("/publications.shtml")
@app.route("/Publications.html")
def publications():
    """
    Publications page
    """
    return render_template('publications.html')


@app.route("/rgm_publications")
@app.route("/rgm_publications.html")
def rgm_publications():
    """
    Special publications page for RGM
    """
    return render_template('rgm_publications.html')


@app.route("/brp_references")
@app.route("/brp_references.html")
def brp_references():
    """
    Special page for KP
    """
    return render_template('brp_references.html')


@app.route("/CCI")
@app.route("/cci")
@app.route("/CCI.html")
@app.route("/cci.html")
@app.route("/cci.shtml")
def cci():
    """
    Info page for Critical Care Informatics
    """
    return render_template('cci.html')


@app.route("/PhysioNet")
@app.route("/Physionet")
@app.route("/physionet")
@app.route("/PhysioNet.html")
@app.route("/Physionet.html")
@app.route("/physionet.html")
@app.route("/physionet.shtml")
def physionet():
    """
    Info page for PhysioNet
    """
    return render_template('physionet.html')


@app.route("/BRP")
@app.route("/brp")
@app.route("/BRP.html")
@app.route("/brp.html")
@app.route("/brp.shtml")
def brp():
    """
    OLD brp page
    """
    return render_template('brp.html')


@app.route("/people")
@app.route("/People")
@app.route("/people.html")
@app.route("/People.html")
@app.route("/people.shtml")
def people():
    """
    Function to display the list of people in the lab.
    The categories are:
        1. General
        2. Colaborating Researcher
        3. Visiting Colleague
        4. Alumni
        5. Grad Student
        6. UROP
        7. Affiliate
        8. Other
    """
    people_list = PersonelModel().get_user_public()
    person = []
    colab = []
    grad = []
    visiting = []
    aff = []
    ids = ""
    for item in people_list:
        # If the person is set as hidden then skip = item[10]
        if item[3] in [1, 3, 5, 7]:
            bio = ""
            ids += "<li><a href='#{0}'>{1}</a></li>".format(item[0], item[2])
            if item[1]:
                if "\n" in item[1] and item[1] is not None:
                    bio_array = item[1].split("\n")
                    for line in bio_array:
                        bio += "<p>{0}</p>".format(line)
                else:
                    bio = "<p style='margin:0 0 0 0;'>{0}</p>".format(item[1])
            else:
                bio = ""
            if item[3] == 1:
                person.append([item[0], bio, item[2], item[3], item[4]])
            elif item[3] == 3:
                visiting.append([item[0], bio, item[2], item[3], item[4]])
            elif item[3] == 5:
                grad.append([item[0], bio, item[2], item[3], item[4]])
            elif item[3] == 7:
                aff.append([item[0], bio, item[2], item[3], item[4]])
        elif item[10] not in ['true', True]:
            colab.append([item[0], item[1], item[2]])
    return render_template('people.html', IDs=ids, Person=person,
                           Visiting=visiting, Grad=grad, Colab=colab, Aff=aff)

###############################################################################
#
# Dashboard pages for the LCP
#
###############################################################################
@app.route("/login")
@app.route("/Login")
@app.route("/login.html")
@app.route("/Login.html")
def login():
    """
    Login function
    """
    session["Username"] = 'ftorres'
    session['URL'] = "https://lcp.mit.edu"
    error, success = status()
    return render_template('admin/login.html', Error=error)


@app.route("/Authenticate", methods=['POST', 'GET'])
def authenticate():
    """
    Auth function
    """
    if request.method == 'GET':
        return redirect('login')
    username = sub(r"[!@#$%^&*()_+\[\]{}:\"?><,/\'\;~` ]", '',
                   request.form.get('Username', None))
    if username is not None and request.form.get('Password', None) is not None:
        success = auth(username, request.form.get('Password', None))
        if success:
            return redirect('dashboard')
    session["ERROR"] = "Incorrect login or password."
    return redirect('login')


@app.route("/dashboard")
@app.route("/dashboard.html")
@login_required
def dashboard():
    """
    LCP Dashboard
    """
    app.logger.info('The user %s is in the dashboard' % session['Username'])

    session.permanent = True
    error = success = status()
    people_list = PersonelModel().get_all()
    user_admin = [session['Username'], False]
    if session['Username'] in ADMIN:
        user_admin = [session['Username'], True]

    personel = {"General": [], 'Alumni': [], "UROP": [], "Affiliate": [],
                "Other": []}

    for indx, item in enumerate(people_list):
        people_list[indx] = list(item)
        people_list[indx][10] = """False"""
        if item[10]:
            people_list[indx][10] = """True"""
        if item[3] in ["1", 1]:
            people_list[indx][3] = " -- General -- "
            personel['General'].append(people_list[indx])
        elif item[3]in ["2", 2]:
            people_list[indx][3] = " -- Collaborating Researcher -- "
            personel['General'].append(people_list[indx])
        elif item[3] in ["3", 3]:
            people_list[indx][3] = " -- Visiting Colleague -- "
            personel['General'].append(people_list[indx])
        elif item[3] in ["4", 4]:
            people_list[indx][3] = " -- Alumni -- "
            personel['Alumni'].append(people_list[indx])
        elif item[3] in ["5", 5]:
            people_list[indx][3] = " -- Graduate Student -- "
            personel['General'].append(people_list[indx])
        elif item[3] in ["6", 6]:
            people_list[indx][3] = " -- UROP -- "
            personel['UROP'].append(people_list[indx])
        elif item[3] in ["7", 7]:
            people_list[indx][3] = " -- Affiliate Researcher -- "
            personel['Affiliate'].append(people_list[indx])
        else:
            people_list[indx][3] = " -- Other -- "
            personel['Other'].append(people_list[indx])
    return render_template('admin/dashboard.html', Error=error,
                           Success=success, Logged_User=user_admin,
                           Personel=personel)


@app.route("/Edit_User_<uid>")
@login_required
def user(uid):
    """
    Populates page to edit a persons information
    """
    app.logger.info('The user {0} is trying to edit the profile id {1}'.format(
        session['Username'], uid))
    session.permanent = True
    error = success = status()
    person = PersonelModel().get_all_from_id(uid)

    if session['Username'] not in ADMIN and person[8] != session['Username']:
        return redirect('dashboard')

    true_false = "<option value='True'>True</option>\
                  <option value='False'>False</option>"
    person[10] = true_false.replace("'{}'".format(person[10]),
                                    "'{}' selected".format(person[10]))
    if person[10]:
        person[10] = "<option value='True' selected>True</option>\
                      <option value='False'>False</option>"

    category = "<option value='1'> -- General -- </option>\
                <option value='2'> -- Collaborating Researcher -- </option>\
                <option value='3'> -- Visiting Colleague -- </option>\
                <option value='4'> -- Alumni -- </option>\
                <option value='5'> -- Graduate Student -- </option>\
                <option value='6'> -- UROP -- </option>\
                <option value='7'> -- Research Affiliate -- </option>\
                <option value='8'> -- Other -- </option>"
    person[3] = category.replace("'{}'".format(person[3]),
                                 "'{}' selected".format(person[3]))

    return render_template('admin/edit.html', Error=error, Success=success,
                           Logged_User=session['Username'], Person=person)

###############################################################################
# 1. General
# 2. Colaborating Researcher
# 3. Visiting Colleague
# 4. Alumni
# 5. Grad Student
# 6. UROP
# 7. Affiliate
# 8. Other
###############################################################################
@app.route("/Submit_User", methods=['POST', 'GET'])
@login_required
def submit_user():
    """
    FUNCTION to handle user edits
    """
    app.logger.info(request.form)
    if request.method == 'POST' and request.form.get("FName"):
        person_info = {'Full_Name': request.form.get('FName', "None"),
                       'Username': request.form.get('Username', "None"),
                       'Status': request.form.get('Status', "None"),
                       'Email': request.form.get('Email', "None"),
                       'Bio': request.form.get('Bio', "None"),
                       'UID': request.form.get('UID', "None"),
                       'Food': request.form.get('Food', "False"),
                       'Hidden': request.form.get('Hidden', "False", ),
                       'y': request.form.get("y"),
                       'x': request.form.get("x"),
                       'height': request.form.get("height"),
                       'width': request.form.get("width")}

        model = PersonelModel()
        success = "empty"
        if request.files.get("picture"):
            # If there is an image, then upload and crop it
            if (person_info["y"] and person_info["x"] and person_info["height"]
                    and person_info["width"]):
                filename = resize_image()
            else:
                # The image should NOT be blank, but its a posibility
                # I am unaware if this if is used
                filename = 'missing.jpg'
                if model.get_picture(person_info["UID"])[1] != '':
                    filename = model.get_picture(person_info["UID"])[1]
                app.logger.error("Problem with the upload, (missing axis)")
                session['ERROR'] = "Error uploading the image."
        else:
            # The image should NOT be blank, but its a posibility
            # I am unaware if this if is used
            filename = 'missing.jpg'
            if model.get_picture(person_info["UID"])[1] != '':
                filename = model.get_picture(person_info["UID"])[1]

        if request.form.get("New_User") in ['1', 1]:
            success = model.new_person(person_info["Full_Name"], filename,
                                       person_info["Status"],
                                       person_info["Email"],
                                       person_info["Bio"])
        else:
            bio = model.get_bio_from_id(person_info["UID"])
            if bio != person_info["Bio"]:
                content = "The Bio of {1} has changed. Please take a look at \
                           the Bio to see if up to standards.\nThe old Bio is:\
                           \n{0}\nThe new Bio is:\n{2}".format(
                               bio, person_info["Full_Name"],
                               person_info["Bio"])
                subject = "Bio changed in the LCP website"
                html_content = content + "The changes are:\n{0}".format(
                    show_diff(bio, person_info["Bio"]))
                send_html_email(subject, content, html_content.replace(
                    '\n', '<br>'), 'noreply@lcp.mit.edu')
            success = model.update(
                person_info["Full_Name"], person_info["Status"], filename,
                person_info["Email"], person_info["Bio"], person_info["UID"],
                person_info["Food"], person_info["Hidden"])
    else:
        return redirect('/dashboard')

    if success:
        session['SUCCESS'] = "The update was successfully done."
        return redirect('dashboard')
    app.logger.error(success)
    session['ERROR'] = "There was an error, please try again."
    return redirect('dashboard')


def status():
    """
    Return if there was an error or successful event
    """
    error = success = False
    if 'ERROR' in session:
        error = session['ERROR']
        session.pop('ERROR', None)
    elif 'SUCCESS' in session:
        success = session['SUCCESS']
        session.pop('SUCCESS', None)
    return error, success


@app.route("/datathon", methods=['POST', 'GET'])
@login_required
def datathon():
    """
    Page to handle datathon access to MIMIC and eICU
    """
    error = success = status()
    model = DatathonModel()

    if request.method == 'POST' and request.form.get("remove_id"):
        remove_id = request.form.get('remove_id', None)
        if model.revoke_bq_access(session['Username'], remove_id):
            datathon_info = model.get_by_id(remove_id)
            revoke_gcp_group_access(datathon_info[3])
            success = "The BigQuery from {0} access has been removed.".format(
                datathon_info[3])

    datathons = model.get_all()
    return render_template('admin/datathons.html', Error=error,
                           Success=success, datathons=datathons)


@app.route("/datathon_add", methods=['POST', 'GET'])
@login_required
def datathon_add():
    """
    Page to handle datathon access to MIMIC and eICU
    """
    var = {}
    if request.method == 'POST' and request.form.get("location"):
        var['location'] = request.form.get('location', None)
        var['contact_name'] = request.form.get('contact_name', None)
        var['contact_email'] = request.form.get('contact_email', None)
        var['google_group'] = request.form.get('google_group', None)
        var['date'] = request.form.get('date', None)
        var['user'] = session['Username']

        if not (valid_email(var['contact_email']) and
                valid_email(var['google_group'])):
            return render_template('admin/datathon_add.html',
                                   Error="Please enter valid emails")

        model = DatathonModel()
        if model.grant_bq_access(var):
            grant_gcp_group_access(var['contact_email'])
            session['SUCCESS'] = "Access was granted."
        else:
            session['ERROR'] = "Error with the dabase, access skipped."
        return redirect('datathon')
    return render_template('admin/datathon_add.html')


def grant_gcp_group_access(email):
    """
    Add a specific email address to a organizational google group
    Returns two things:
        The first argument is if access was awarded.
        The second argument is if the access was awarded in a previous time.
    """
    service = build_service()
    try:
        outcome = service.members().insert(groupKey=DATATHON_GROUP, body={
            "email": email, "delivery_settings": "NONE"}).execute()
        if outcome['role'] == "MEMBER":
            session['SUCCESS'] = 'Access has been granted to {0}'.format(email)
            return True
        session['ERROR'] = 'Error granting access to {0}'.format(email)
        return False
    except HttpError as error:
        if json.loads(error.content)['error']['message'] != 'Member already exists.':
            raise error


def revoke_gcp_group_access(email):
    """
    Add a specific email address to a organizational google group
    Returns two things:
        The first argument is if access was awarded.
        The second argument is if the access was awarded in a previous time.
    """
    service = build_service()
    try:
        outcome = service.members().delete(groupKey=DATATHON_GROUP,
                                           memberKey=email).execute()
        if outcome == '':
            session['SUCCESS'] = 'Access has been granted to {0}'.format(email)
            return True
        session['ERROR'] = 'Error granting access to {0}'.format(email)
        return False
    except HttpError as error:
        if json.loads(error.content)['error']['message'] != 'Resource Not Found: memberKey':
            raise error


def build_service():
    """
    Builds the GCP service to add and remove emails to admin.google.com
    """
    if not path.isfile(SERVICE_ACCOUNT_KEY):
        raise Exception("The GCP access key file does not exists.")

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL, SERVICE_ACCOUNT_KEY, GCP_SECRET_KEY,
        scopes=['https://www.googleapis.com/auth/admin.directory.group'])
    credentials = credentials.create_delegated(GCP_DELEGATION_EMAIL)
    return build('admin', 'directory_v1', credentials=credentials)


def valid_email(email):
    """
    Validates emails
    """
    regex = r'\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    if not search(regex, email):
        app.logger.info("Invalid email: {}".format(email))
        return False
    return True


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', port=8083, threaded=True, debug=True)
