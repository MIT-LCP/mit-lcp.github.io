from flask import Flask, render_template, redirect, request, session, g, url_for
from logging.handlers import RotatingFileHandler
from datetime import timedelta, datetime, date
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from email.message import EmailMessage
from email.mime.text import MIMEText
from os import path, remove
from functools import wraps
from smtplib import SMTP
from uuid import uuid4
from Postgres import *
from PIL import Image
from re import sub
import traceback
import simplepam
import logging
import difflib

app = Flask(__name__) # Add the debug if you are running debugging mode

app.config.update(
        PERMANENT_SESSION_LIFETIME = timedelta(seconds=3000),
        SECRET_KEY = 'mf}7WwDxTm8ik}ipULrYgSWzfxutj|zDo1n(h+abvE&$aM)?O$8R>qUtE)?CyOQ)*6YwADN!IHLy+TE^K1>>1^riVxme**JBH!+N',
        MAX_CONTENT_PATH = 5 * 1024 * 1024,
        TEMPLATES_AUTO_RELOAD = True,
        UPLOAD_FOLDER = "static/images/"
        )

app.jinja_env.auto_reload = True

# Set logging information
handler = RotatingFileHandler('/var/log/flask/lcp_website.log', maxBytes=10000000, backupCount=2)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"))
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

ADMIN = ["ftorres", "rgmark", "kpierce", "alistairewj", "tpollard"]
EMAIL_RECIPIENTS = ['ftorres@mit.edu', 'kpierce@mit.edu']
PRIMARY_ADMIN = ['ftorres@mit.edu']

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # if user is not logged in, redirect to login page
        if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
            return redirect(url_for('login'))
        # make user available down the pipeline via flask.g
        g.username = session['Username']
        # finally call f. f() now haves access to g.user
        return f(*args, **kwargs)
    return wrap

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.errorhandler(500)
def internal_server_error(error):
    """
    This is the page for handling internal server error, there will be a log in apache and email generated
    """
    app.logger.error("500 - Internal Server Error - {0}".format(request.path))
    app.logger.error("{}".format(error))
    tb = str(traceback.format_exc())
    Content = "Hi,\n\nThere was a internal server error on the Flask app running the LCP website.\n"
    Content += "The time of this error is: {0}\n".format(datetime.now())
    Content += "The error messege is: {0}\n".format(str(error))
    Content += "Error traceback:\n{0}".format(tb)
    send_email("Internal Server Error - Flask LCP", Content, 'noreply_error@lcp.mit.edu')
    if 'Username' in session:
        Content += "\n\nThe user tha triggered this error is: {0}\n\nThanks!".format(session['Username'])
    send_email("Internal Server Error - Flask LCP - {0}".format(request.path), Content, 'noreply_error@lcp.mit.edu')

    return render_template('500.html')#, 404

@app.route('/robots.txt')
def send_text_file():
    return app.send_static_file('robots.txt')

def send_email(Subject, Content, sender, rec=None):
    """
    This functions sends an email, takes subject, content, sender and recipients
    The recipients has to be a list of emails, even is there is only one
    """
    server = SMTP('127.0.0.1')
    msg = MIMEText(Content, 'plain')
    recipients = PRIMARY_ADMIN
    if rec != None:
        recipients = rec
    msg['Subject'] = Subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()


def send_html_email(Subject, Content, html_Content, sender, rec=None):
    """
    This functions sends an email, takes subject, content, sender and recipients
    The recipients has to be a list of emails, even is there is only one

    Here a HTML email will be sent.
    """
    msg = MIMEMultipart('alternative')
    recipients = PRIMARY_ADMIN
    if rec != None:
        recipients = rec
    msg['Subject'] = Subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    html = """\
    <html>
      <head></head>
      <body>
        {0}
      </body>
    </html>
    """.format(html_Content)
    part1 = MIMEText(Content, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    server = SMTP('192.168.1.164')
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()

def Checkout_form(Vars):
    '''
    Checkout form function that will be called in the submittion of the 'info/submit'
    '''
    SUBJECT = 'LCP checkout form - {0}'.format(Vars['email'])
    Content = "\nLastname: {0}\nFirstname: {1}\nEnd date: {2}\n\
    Archive location:\nMachine name: {3}\nFilepath: {4}\n\
    Special instructions: {5}\nNew preferred e-mail address: {6}\n\
    Valid from (date): {7}\nNew office address: {8}\nValid from (date): {9}\n\
    New home address: {10}\nNew telephone number(s): {11}\nAnything else: {12}\n".format(
        Vars['lastname'], Vars['firstname'], Vars['enddate'], 
        Vars['machine'], Vars['filepath'], Vars['instructions'], Vars['email'], 
        Vars['email-when'], Vars['office-address'], Vars['office-when'], 
        Vars['home-address'], Vars['phone'], Vars['extra'])

    # Log the variables in case an error occurs.
    app.logger.info("A person did the checkout form. Variables are the \
        following: {}".format(Vars))

    # Insert the checkout form into the database
    model = SimpleModel()
    result = model.Insert_line_exit(Vars)

    send_email(Subject=SUBJECT, Content=Content, sender=Vars['email'], 
        rec=EMAIL_RECIPIENTS)

    if result != True:
        app.logger.error("There was an error in the postgres insert of the Checkout_form\n{0}\n{1}".format(Content, str(result)))
        send_email("There was an error in the Checkout form line insert", result, 'noreply@lcp.mit.edu')
        return result, False
    return Content, True

def Registration_form(Vars, request):
    '''
    Checkin form function that will be called in the submittion of the 'info/submit'
    '''
    Picture = 'missing.jpg'

    if request.files.get("picture"):
        app.logger.info("Image found in the registration form.")
        if Vars["y"] and Vars["x"] and Vars["height"] and Vars["width"]:
            Picture = resize_image(request)
        else:
            app.logger.error("There was a problem with the picture upload, missing axis")
            session['ERROR'] = "There was a problem with the picture, skipping it."

    # Set the content ofr the email, and the display page summary - The display page summary just shows what the user submitted
    SUBJECT = 'LCP registration form - {0}'.format(Vars['email'])

    Content = "\nFull Name: {0} {1}\n\nStart date: {2}\nMIT username: {3}\n\
    LCP username: {4}\nMIT ID number: {5}\nPreferred e-mail address: {6}\n\
    Office address: {7}\nHome address: {8}\nTelephone number(s): {9}\n\
    Emergency contact: {10}\nCurrent project(s) in LCP: {11}\nFocus of research: {12}\n\
    Bio: {13}\nPicture:{14}\nEHS training date: {15}\nHuman studies training date: {16}\n\
    Anything else: {17}\n".format(Vars['firstname'], Vars['lastname'], 
        Vars['startdate'], Vars['username'], Vars['lcp_username'], Vars['id'], 
        Vars['email'], Vars['office-address'], Vars['home-address'], Vars['phone'], 
        Vars['emergency-contact'], Vars['research'], Vars['Other'], Vars['Bio'],
        Picture, Vars['ehs_training'], Vars['human_studies_training'], Vars['extra'])
   

    app.logger.info("A person did the checkin form. Variables are the following:\
     {}".format(Vars))

    # Inserts the new user to the DB
    model = SimpleModel()
    result = model.Insert_line_reg(Vars, Picture)
    # Alert that the users have been submitted
    send_email(Subject=SUBJECT, Content=Content, sender=Vars['email'], rec=EMAIL_RECIPIENTS)

    if result != True:
        app.logger.error("There was an error in the postgres insert of the Registration_form\n{0}\n{1}".format(Content, str(result)))
        send_email("There was an error in the Checkin form line insert", result, 'noreply@lcp.mit.edu')
        return result, False
    return Content, True

def resize_image(request):
    '''
    Function that takes a image to crop it.
    '''
    x = float(request.form.get('x', None))
    y = float(request.form.get('y', None))
    w = float(request.form.get('width', None))
    h = float(request.form.get('height', None))
    f = request.files['picture']
    UID = request.form.get('UID', None)
    
    status = username = ''

    if UID != None:
        status, username = Personel_Model().GetUsernameByID(UID)
    else:
        username = request.form.get('email', None).split("@")[0]

    Filename = username + '.' + f.filename.split('.')[-1]

    if path.exists(app.config['UPLOAD_FOLDER'] + Filename):
        remove(app.config['UPLOAD_FOLDER'] + Filename)

    image = Image.open(f)
    image = image.crop((x, y, w+x, h+y))
    image = image.resize((200, 200), Image.ANTIALIAS)

    image.save(app.config['UPLOAD_FOLDER'] + Filename)

    return Filename

def Auth(Username, Password):
    '''
    Authentication function against the system users.
    '''
    result = simplepam.authenticate(str(Username), str(Password))
    Personel = Personel_Model()
    if result:
        session["Username"] = Username
        session["SID"] = str(uuid4())
        session['URL'] = "https://lcp.mit.edu"
        return True
    else:
        app.logger.error('Incorrect password or username: {0} Error: {1}'.format(
            Username, result))
        return False

def is_Date(date_string):
    try:
        date_obj = datetime.strptime(date_string, '%m/%d/%Y')
        return True
    except Exception as e:
        app.logger.error(e)
        return False

def show_diff(text, n_text):
    """
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<font color=red>^{0}</font>".format(seqm.b[b0:b1]))
        elif opcode == 'delete':
            output.append("<font color=blue>^{0}</font>".format(seqm.a[a0:a1]))
        elif opcode == 'replace':
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append("<font color=green>^{0}</font>".format(seqm.b[b0:b1]))
        else:
            raise (RuntimeError, "unexpected opcode")
    return ''.join(output)

###############################################################################
#
# Pages for the LCP registration, checkout and basic information for the lab.
#
###############################################################################
@app.route("/info/")#Index page
@app.route("/info/index")
@app.route("/info/index.html")
def lab_index():#render the index page information
    return render_template('info/index.html')

@app.route("/info/reg_form")
@app.route("/info/reg_form.html")
def reg_form():#render the index page information
    return render_template('info/registration_form.html')

@app.route("/info/intro_to_Mark_lab")
@app.route("/info/intro_to_Mark_lab.html")
def intro_to_Mark_lab():#render the index page information
    return render_template('info/intro_to_Mark_lab.html')

@app.route("/info/check_out_form")
@app.route("/info/check_out_form.html")
def check_out_form():#render the index page information
    return render_template('info/check_out_form.html')

@app.route("/info/submit", methods=['POST'])
def submit():#render the index page information
    """
    This form accept both registration and checkout form.
    """
    app.logger.info("Person doing the registration\n")
    app.logger.info(request.form)
    Vars = {'firstname': request.form.get('firstname', None),
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
    'human_studies_training': request.form.get('human_studies_training', None),
    'extra': request.form.get('extra', None),
    'enddate': request.form.get('enddate',None),
    'machine': request.form.get('machine', None),
    'filepath': request.form.get('filepath', None),
    'instructions': request.form.get('instructions', None),
    'email-when': request.form.get('email-when', None),
    'office-when': request.form.get('office-when', None),
    'y': request.form.get("y", None), 'x': request.form.get("x", None),
    'height': request.form.get("height", None), 'width': request.form.get("width", None)}

    Content = ''
    if request.form.get('Registration_form', 'None') != 'None':
        Content, valid = Registration_form(Vars, request)
    elif request.form.get('Checkout_form', 'None') != 'None':
        Content, valid = Checkout_form(Vars)
    else:
        return render_template('info/index.html')

    return render_template('info/submit.html', Content=Content.replace("\n","<br>"))

###############################################################################
#
# Main pages for the LCP website
#
###############################################################################
@app.route("/")#Index page
@app.route("/index")
@app.route("/index.html")
@app.route("/index.shtml")
def index():#render the index page information
    return render_template('index.html')

@app.route("/projects")#Index page
@app.route("/Projects")
@app.route("/Projects.html")
@app.route("/projects.html")
@app.route("/projects.shtml")
@login_required
def Projects():#render the index page information
    projects = Project_Model().GetAllWebsite()
    return render_template('projects.html', Projects=projects)

@app.route("/publications")#Index page
@app.route("/Publications")
@app.route("/publications.html")
@app.route("/publications.shtml")
@app.route("/Publications.html")
def Publications():#render the index page information
    return render_template('publications.html')

@app.route("/rgm_publications")#Index page
@app.route("/rgm_publications.html")
def rgm_publications():#render the index page information
    return render_template('rgm_publications.html')

@app.route("/brp_references")#Index page
@app.route("/brp_references.html")
def brp_references():#render the index page information
    return render_template('brp_references.html')

@app.route("/CCI")#Index page
@app.route("/cci")
@app.route("/CCI.html")
@app.route("/cci.html")
@app.route("/cci.shtml")
def CCI():#render the index page information
    return render_template('cci.html')

@app.route("/PhysioNet")#Index page
@app.route("/Physionet")
@app.route("/physionet")
@app.route("/PhysioNet.html")
@app.route("/Physionet.html")
@app.route("/physionet.html")
@app.route("/physionet.shtml")
def Physionet():#render the index page information
    return render_template('physionet.html')

@app.route("/BRP")#Index page
@app.route("/brp")
@app.route("/BRP.html")
@app.route("/brp.html")
@app.route("/brp.shtml")
def BRP():#render the index page information
    return render_template('brp.html')

@app.route("/people")#Index page
@app.route("/People")
@app.route("/people.html")
@app.route("/People.html")
@app.route("/people.shtml")
def people():#render the index page information
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
    People = Personel_Model().GetAllWeb()

    #Creating 5 empty arrays
    Person, Colab, Grad, Visiting, Aff = ([] for i in range(5))

    IDs = ""
    for item in People:
        if item[10] == True or item[10] == "True" or item[10] == 1 or item[10] == 'true':
            pass
        elif item[3] in [1, 3, 5, 7]: #check the number value before this function
            Bio = ""                  # This here is to display the Bio and the top banner witht he names
            IDs += "<li><a href='#{0}'>{1}</a></li>".format(item[0], item[2])
            if item[1]:
                if "\n" in item[1] and item[1] != None:
                    Bio_Array = item[1].split("\n")
                    for line in Bio_Array:
                        Bio += "<p>{0}</p>".format(line)
                else:
                    Bio = "<p style='margin:0 0 0 0;'>{0}</p>".format(item[1])
            else:
                Bio = ""
            if item[3] == 1:
                Person.append([item[0], Bio, item[2], item[3], item[4]])
            elif item[3] == 3:
                Visiting.append([item[0], Bio, item[2], item[3], item[4]])
            elif item[3] == 5:
                Grad.append([item[0], Bio, item[2], item[3], item[4]])
            elif item[3] == 7:
                Aff.append([item[0], Bio, item[2], item[3], item[4]])
        else:
            Colab.append([item[0], item[1], item[2]])
    return render_template('people.html', IDs=IDs, Person=Person, Visiting=Visiting, Grad=Grad, Colab=Colab, Aff=Aff)

###############################################################################
#
# Dashboard pages for the LCP
#
###############################################################################

@app.route("/login")#Signup page
@app.route("/Login")#Signup page
@app.route("/login.html")#Signup page
@app.route("/Login.html")#Signup page
def login():
    if 'ERROR' in session:
        Error = session['ERROR']
        session.pop('ERROR', None)
        app.logger.error('Loggin error: %s' % Error)
        return render_template('admin/login.html', Error=Error)
    else:
        return render_template('admin/login.html')

@app.route("/Authenticate", methods=['POST','GET'])#Signup page
def Authenticate():
    if request.method == 'GET':
        return redirect('login')
    Username = sub(r"[!@#$%^&*()_+\[\]{}:\"?><,/\'\;~` ]", '', request.form.get('Username', None))
    if Username != None and request.form.get('Password', None) != None:
        Success = Auth(Username, request.form.get('Password', None))
        if Success:
            return redirect('dashboard')
    session["ERROR"] = "Incorrect login or password."
    return redirect('login')


@app.route("/User_List")
@app.route("/User_List.html")
@login_required
def User_List():
    E = S = P_Output = ''
    People      = Personel_Model().GetAll2()
    Logged_User = []
    if session['Username'] in ADMIN:
        Logged_User = [session['Username'], True]
    else:
        Logged_User = [session['Username'], False]
    for indx, item in enumerate(People):
        People[indx] = list(People[indx])
        if item[1] == 1:
            People[indx][1] = 'Lab Personel'
        elif item[1] == 3:
            People[indx][1] = 'Visiting Colleage'
        elif item[1] == 5:
            People[indx][1] = 'Graduate Student'
        elif item[1] == 6:
            People[indx][1] = 'UROP Student'
    return render_template('admin/User_list.html', Error=E, Success=S, Users=People, Logged_User=Logged_User)

@app.route("/new_project", methods=['POST','GET'])
@login_required
def manage_projects():
    app.logger.info(request.form)
    if request.method == 'POST':
        Project_Info = {'p_name': request.form.get('p_name', "None").replace("'","''").rstrip(),  
        'p_desc':    request.form.get('p_desc', "None").replace("'","''").rstrip(), 
        'p_contact': request.form.get('p_contact', "None").replace("'","''").rstrip(), 
        'p_email':   request.form.get('p_email', "None"),
        'display_p': request.form.get('display_p', "None"), 
        'active_p':  request.form.get('active_p', "False"),
        'PID':       request.form.get('PID', "False"),
        'submitting_user': session['Username']}

        if request.form.get("P_new") == '1' or request.form.get("P_new") == 1:
            Success = Project_Model().New_ALL(Project_Info)
            status, Full_name = Personel_Model().GetNameByUsername(Project_Info['submitting_user'])
            if Success and status:
                Content = "A new project was submitted by {0}. \nThe project information is the following,\nTitle: {1}\nAbstract: {2}\nContact person: {3}\nContact email: {4}".format(Full_name, Project_Info['p_name'], Project_Info['p_desc'], Project_Info['p_contact'], Project_Info['p_email'])
                send_email('New Project added for review - ', Content, 'contact@lcp.mit.edu')
            else:
                session['Error'] = Success
        elif request.form.get("PID", None) != None:
            Success = Project_Model().Update_ALL(Project_Info)
    return redirect('dashboard')
    #return render_template('edit_project.html', Error=E, Success=S, Logged_User=session['Username'], Person=Person)

@app.route("/dashboard")
@app.route("/dashboard.html")
@login_required
def dashboard():
    app.logger.info('The user %s is in the dashboard' % session['Username'])

    session.permanent = True
    Error = Success = ''
    if 'ERROR' in session:
        Error = session['ERROR']
        session.pop('ERROR', None)
    elif 'SUCCESS' in session:
        Success = session['SUCCESS']
        session.pop('SUCCESS', None)

    UserModel   = Personel_Model()
    People      = UserModel.GetAll()
    Logged_User = [session['Username'], False]

    Personel = {"General":[],'Alumni':[],"UROP":[],"Affiliate":[],"Other":[]}

    if session['Username'] in ADMIN:
        Logged_User = [session['Username'], True]

    for indx, item in enumerate(People):
        People[indx] = list(item)
        if item[10] == True:
            People[indx][10] = """True"""
        else:
            People[indx][10] = """False"""
        if item[3] == 1 or item[3] == "1":
            People[indx][3] = " -- General -- "
            Personel['General'].append(People[indx])
        elif item[3] == 2 or item[3] == "2":
            People[indx][3] = " -- Collaborating Researcher -- "
            Personel['General'].append(People[indx])
        elif item[3] == 3 or item[3] == "3":
            People[indx][3] = " -- Visiting Colleague -- "
            Personel['General'].append(People[indx])
        elif item[3] == 4 or item[3] == "4":
            People[indx][3] = " -- Alumni -- "
            Personel['Alumni'].append(People[indx])
        elif item[3] == 5 or item[3] == "5":
            People[indx][3] = " -- Graduate Student -- "
            Personel['General'].append(People[indx])
        elif item[3] == 6 or item[3] == "6":
            People[indx][3] = " -- UROP -- "
            Personel['UROP'].append(People[indx])
        elif item[3] == 7 or item[3] == "7":
            People[indx][3] = " -- Affiliate Researcher -- "
            Personel['Affiliate'].append(People[indx])
        else:
            People[indx][3] = " -- Other -- "
            Personel['Other'].append(People[indx])

    Projects = Project_Model().GetAll()

    return render_template('admin/dashboard.html', Error=Error, Success=Success, Logged_User=Logged_User, Personel=Personel, Projects=Projects)

@app.route("/Edit_Project_<id>")
@login_required
def project(id):
    """
    FUNCTION to do project edits
    """
    app.logger.info('The user {0} is trying to edit a project ID {1}'.format(session['Username'], id))
    session.permanent = True

    E = S = P_Output = ''
    if 'ERROR' in session:
        E = session['ERROR']
        session.pop('ERROR', None)
    elif 'SUCCESS' in session:
        S = session['SUCCESS']
        session.pop('SUCCESS', None)
    if session['Username'] in ADMIN:
        Admin = 1
    else:
        Admin = 0
    status, Project = Project_Model().GetAllByID(id)
    if status:
        return render_template('admin/edit_project.html', Error=E, Success=S, Logged_User=session['Username'], Project=Project, Admin=Admin)
    app.logger.error("There was an error trying to get a specific project, the project doesnt seem to exist, the error code is as follows.")
    app.logger.error(status)
    E = status
    return render_template('admin/edit_project.html', Error=E, Success=S, Logged_User=session['Username'])

@app.route("/Edit_User_<id>")
@login_required
def user(id):
    app.logger.info('The user {0} is trying to edit the profile id {1}'.format(session['Username'], id))
    session.permanent = True
    E = S = P_Output = ''
    if 'ERROR' in session:
        E = session['ERROR']
        session.pop('ERROR', None)
    elif 'SUCCESS' in session:
        S = session['SUCCESS']
        session.pop('SUCCESS', None)
    Person = Personel_Model().GetAllByID(id)

    if session['Username'] not in ADMIN and Person[8] != session['Username']:
        return redirect('dashboard')

    if Person[10] == True:
        Person[10] = "<option value='True' selected>True</option><option value='False'>False</option>"
    else:
        Person[10] = "<option value='True'>True</option><option value='False' selected>False</option>"
    if Person[3] == 1 or Person[3] == "1":
        Person[3] = "<option value='1' selected> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>"
    elif Person[3] == 2 or Person[3] == "2":
        Person[3] = "<option value='1'> -- General -- </option><option value='2' selected> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>"
    elif Person[3] == 3 or Person[3] == "3":
        Person[3] = "<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3' selected> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>"
    elif Person[3] == 4 or Person[3] == "4":
        Person[3] = "<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4' selected> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>"
    elif Person[3] == 5 or Person[3] == "5":
        Person[3] = "<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5' selected> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>"
    elif Person[3] == 6 or Person[3] == "6":
        Person[3] = "<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6' selected> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>"
    elif Person[3] == 7 or Person[3] == "7":
        Person[3] = "<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7' selected> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>"
    else:
        Person[3] = "<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8' selected> -- Other -- </option>"

    return render_template('admin/edit.html', Error=E, Success=S, Logged_User=session['Username'], Person=Person)

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
@app.route("/Submit_User", methods=['POST','GET'])#Signup page
@login_required
def Submit_User():
    """
    FUNCTION to handle user edits
    """
    app.logger.info(request.form)
    if request.method == 'POST' and request.form.get("FName"):
        Person_Info = {'Full_Name': request.form.get('FName', "None").replace("'","''"), 'Username': request.form.get('Username', "None").replace("'","''").rstrip(), 'Status': request.form.get('Status', "None"), 'Email': request.form.get('Email', "None"), 'Bio': request.form.get('Bio', "None").replace("'","''"), 'UID': request.form.get('UID', "None"), 'Food': request.form.get('Food', "False"), 'Hidden': request.form.get('Hidden', "False", ), 'y':request.form.get("y"), 'x': request.form.get("x"), 'height': request.form.get("height"), 'width': request.form.get("width")}
        Model = Personel_Model()
        Success = "empty"
        if request.files.get("picture"):
            if Person_Info["y"] and Person_Info["x"] and Person_Info["height"] and Person_Info["width"]:
                filename = resize_image(request)
            else:
                if Model.GetPicture(Person_Info["UID"])[1] == '':
                    filename = 'missing.jpg'
                else:
                    filename = Model.GetPicture(Person_Info["UID"])[1]
                app.logger.error("There was a problem with the picture upload, no Y axis")
                session['ERROR'] = "There was a problem with the picture, skipping it."
        else:
            if Model.GetPicture(Person_Info["UID"])[1] == '':
                filename = 'missing.jpg'
            else:
                filename = Model.GetPicture(Person_Info["UID"])[1]

        if request.form.get("New_User") == '1' or request.form.get("New_User") == 1:
            Success = Model.New_ALL(Person_Info["Full_Name"], Person_Info["Status"], filename, Person_Info["Email"], Person_Info["Bio"])
        else:
            status, Bio = Model.GetBioByID(Person_Info["UID"])
            if Bio != Person_Info["Bio"]:
                Content = "The Bio of {0} has changed. Please take a look at the Bio to see if up to standards.\n\n".format(Person_Info["Full_Name"])
                Content += "The old Bio is:\n{0}\n\nThe new Bio is:\n{1}\n\n".format(Bio, Person_Info["Bio"])
                Subject = "Bio changed in the LCP website"
                html_Content = Content + "The changes are:\n{0}\n\nThanks!".format(show_diff(Bio, Person_Info["Bio"]))
                send_html_email(Subject, Content, html_Content.replace('\n','<br>'), 'noreply@lcp.mit.edu')
            Success = Model.Update_ALL(Person_Info["Full_Name"], Person_Info["Status"], filename, Person_Info["Email"], Person_Info["Bio"], Person_Info["UID"], Person_Info["Food"], Person_Info["Hidden"])
    else:
        return redirect('/dashboard')

    if (Success == 1 or Success == True):
        session['SUCCESS'] = "The update was successfully done."
        return redirect('dashboard')
    else:
        app.logger.error(Success)
        session['ERROR'] = "There was an error, please try again."
        return redirect('dashboard')

###############################################################################
## 
## From here down is DUA related
## 
###############################################################################
@app.route("/get_info", methods=['POST'])
@login_required
def get_info():
    last  = request.form.get('last_name', None)
    first = request.form.get('first_name', None)
    email = request.form.get('email', None)

    mimic_model = MIMIC_Model()

    if first is not None and first != '':
        List = mimic_model.get_like_name(first)
    elif last is not None and last != '':
        List = mimic_model.get_like_last(last)
    elif email is not None and email != '':
        List = mimic_model.get_like_email(email)
    else:
        List = []

    Line = ''
    for person in List:
        edit = "<a href='edit_dua_{0}' class='btn btn-warning'>Edit</a>".format(person[10])
        person = list(person)
        for indx, item in enumerate(person):
            if item == 'None' or item == None:
                person[indx] = ''
            elif (indx == 4 or indx == 5) and len(item) > 5 and not is_Date(item):
                tmp = item.replace(',','').split()
                day = str(datetime.strptime(tmp[1],'%b').month) + '/' + str(tmp[0]) + '/' + str(tmp[2])
                person[indx] = day
        Line += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>".format(person[0], person[1], person[2], person[4], person[5], person[8], person[7], edit)

    return Line

@app.route("/edit_dua_<ID>", methods=['POST','GET'])
@login_required
def Edit_dua_person(ID):
    E = S = ''
    mimic_model = MIMIC_Model()
    try:
        type(int(ID))
    except:
        Total = mimic_model.get_total()
        return render_template('admin/duas.html', Error=E, Success=S, Logged_User=session['Username'],total=Total)

    app.logger.info('{0}: User {1} is looking at the duas user number {2}.'.format(datetime.now(), session['Username'], ID))

    if request.method == 'POST' and request.form.get("Email"):
        eicu_A  = request.form.get('eicu_A', None)
        MIMIC_A = request.form.get('MIMIC_A', None)
        AWS = request.form.get('AWS', None)
        GEmail = request.form.get('GEmail', None)
        Email = request.form.get('Email', None)
        LName = request.form.get('LName', None)
        FName = request.form.get('FName', None)
        UID   = request.form.get('UID', None)
        Other = request.form.get('Other', None)
        app.logger.info('The variables in the post are: {0}'.format(request.form))
        if is_Date(MIMIC_A) and FName and LName and Email and UID:
            result = mimic_model.alter_person(FName, LName, Email, MIMIC_A, eicu_A, AWS, GEmail, Other, UID)
            app.logger.info('The form result of the DUA edit was: {0}'.format(result))
            if result:
                S = "Updated"
                Total = mimic_model.get_total()
                return render_template('admin/duas.html', Error=E, Success=S, Logged_User=session['Username'],total=Total)
            else:
                E = "Error updating the person"

    Person = mimic_model.get_by_id(ID)
    if Person:
        Person = list(Person)
    else:
        Total = mimic_model.get_total()
        return render_template('admin/duas.html', Error=E, Success=S, Logged_User=session['Username'],total=Total)

    for indx, item in enumerate(Person):
        if item == 'None' or item == None:
            Person[indx] = ''
        elif (indx == 4 or indx == 5) and len(item) > 5 and not is_Date(item):
            tmp = item.replace(',','').split()
            day = str(datetime.strptime(tmp[1],'%b').month) + '/' + str(tmp[0]) + '/' + str(tmp[2])
            Person[indx] = day
    return render_template('admin/edit_dua_person.html', Error=E, date=date, Success=S, Logged_User=session['Username'], Person=Person)

@app.route("/duas")#Signup page
@login_required
def dua_dashboard():
    """
    FUNCTION to handle user edits
    """
    E = S = ''
    mimic_model = MIMIC_Model()
    app.logger.info('{0}: User {1} is looking at the duas.'.format(datetime.now(), session['Username']))

    Total = mimic_model.get_total()

    return render_template('admin/duas.html', Error=E, Success=S, Logged_User=session['Username'],total=Total)

@app.route("/log_info")#Signup page
@login_required
def log_info():
    """
    FUNCTION to handle user edits
    """
    logs = MIMIC_Model().get_all_logs()
    people = {}
    for item in logs:
        if item[5] not in people:
                people[item[5]]=[[item[2],item[4],item[1].replace(microsecond=0),item[0],item[3]]]
        else:
            people[item[5]].append([item[2],item[4],item[1].replace(microsecond=0),item[0],item[3]])

    return render_template('admin/logs.html', logs=logs, people=people)



if __name__ == "__main__":#RUN THE APP in port 8083
    # Once the templates are edited, this is needed to refresh the HTML automaticly
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', port=8083, threaded=True)#, debug=True)
    
