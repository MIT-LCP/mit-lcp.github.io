#!/usr/bin/env python
# -*- coding: utf-8 -*-
from email.mime.text import MIMEText
from datetime import datetime
from smtplib import SMTP
import traceback
import os

from flask import Flask, render_template, redirect, request, session, url_for, Response
from werkzeug.wsgi import DispatcherMiddleware
from PIL import Image
import yaml

from Postgres import PersonelModel

app = Flask(__name__)
if app.config['ENV'] == 'production':
    app.config.from_object('config.ProductionConfig')
elif app.config['ENV'] == 'staging':
    app.wsgi_app = DispatcherMiddleware(app, {'/lcp_dev': app.wsgi_app})
else:
    app.config.from_object('config.DevConfig')


def _data():
    data = {}
    return data


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
    LCP website. \nThe time of this error is: {0}\nError traceback:\n{1}\
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
    if app.config['ENV'] == 'production':
        return app.send_static_file('robots.txt')
    return Response("User-agent: *\nDisallow: /", mimetype='text/plain')


def send_email(subject, content, sender, rec=None):
    """
    Send plain text email
    """
    server = SMTP('127.0.0.1')
    msg = MIMEText(content, 'plain')
    recipients = app.config['PRIMARY_ADMIN']
    if rec is not None:
        recipients = rec
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()


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
    if os.path.exists(app.config['UPLOAD_FOLDER'] + filename):
        os.remove(app.config['UPLOAD_FOLDER'] + filename)

    image = Image.open(file)
    image = image.crop((x_axis, y_axis, width+x_axis, height+y_axis))
    image = image.resize((200, 200), Image.ANTIALIAS)
    image.save(app.config['UPLOAD_FOLDER'] + filename)
    return filename


def get_news_data():
    """
    Retrieve and process the news data
    """
    data = _data()

    path = "sitedata"
    fn = "news.yml"

    with open(os.path.join(path, fn), 'r') as f:
        data["news"] = yaml.safe_load(f)

    years = []
    for i,post in enumerate(data['news']['news_items']):
        # Gives unique names to each news item to create links later
        data['news']['news_items'][i]['post_number'] = 'news_' + str(i)
        # List of all the years for the news items
        years.append(post['date'].split('-')[0])

    data['news']['tag_info'] = {
        'year': sorted(set(years), reverse=True)
    }

    return data


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
               rec=app.config['EMAIL_RECIPIENTS'])

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
               rec=app.config['EMAIL_RECIPIENTS'])

    if result is not True:
        app.logger.error("There was an error in the postgres insert of the \
                         Registration_form\n{0}\n{1}".format(content, result))
        send_email("There was an error in the Checkin form line insert",
                   result, 'noreply@lcp.mit.edu')
        return result
    return content


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
    data = get_news_data()

    return render_template('index.html', **data)


@app.route("/about")
@app.route("/about.html")
@app.route("/about.shtml")
def about():
    """
    About page
    """
    return render_template('about.html')


@app.route("/publications")
@app.route("/publications.html")
@app.route("/publications.shtml")
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


@app.route("/mimic")
@app.route("/mimic.html")
@app.route("/mimic.shtml")
def mimic():
    """
    Info page for Critical Care Informatics
    """
    return render_template('mimic.html')


@app.route("/physionet")
@app.route("/physionet.html")
@app.route("/physionet.shtml")
def physionet():
    """
    Info page for PhysioNet
    """
    return render_template('physionet.html')


@app.route("/brp")
@app.route("/brp.html")
@app.route("/brp.shtml")
def brp():
    """
    OLD brp page
    """
    return render_template('brp.html')


@app.route("/people")
@app.route("/people.html")
@app.route("/people.shtml")
def people():
    """
    Display a list of people.
    """
    data = _data()

    path = 'sitedata'
    fn = 'people.yml'

    with open(os.path.join(path, fn), 'r') as f:
        data['people'] = yaml.safe_load(f)

    return render_template('people.html', **data)

@app.route("/news")
@app.route("/news.html")
@app.route("/news.shtml")
def news():
    """
    Display a list of news items.
    """
    data = get_news_data()
    return render_template('news.html', **data)


@app.route("/<news_id>")
def news_item(news_id):
    """
    Display an individual news item.
    """
    news = get_news_data()

    post = [x for x in news['news']['news_items']
            if x['post_number'] == news_id]

    if post:
        data = {}
        data['post'] = post[0]
        return render_template("news_post.html", **data)
    else:
        return render_template('404.html')


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', port=8083, threaded=True, debug=True)
