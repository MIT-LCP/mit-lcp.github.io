from flask import Flask, render_template, redirect, request, session, Session#,  escape, url_for, jsonify, Session, g
from logging.handlers import RotatingFileHandler
from datetime import timedelta, datetime, date
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from smtplib import SMTP
from uuid import uuid4
from Postgres import *
from PIL import Image
from os import path, remove
from re import sub
import simplepam, logging, traceback, random, string, sys, re, os, difflib

# Change the logger output file and schema

handler = RotatingFileHandler('/var/log/flask/lcp_website.log', maxBytes=10000000, backupCount=2)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"))

app = Flask(__name__) # Add the debug if you are running debugging mode

app.config.update(
        PERMANENT_SESSION_LIFETIME = timedelta(seconds=3000),
        SECRET_KEY = 'mf}7WwDxTm8ik}ipULrYgSWzfxutj|zDo1n(h+abvE&$aM)?O$8R>qUtE)?CyOQ)*6YwADN!IHLy+TE^K1>>1^riVxme**JBH!+N',
        MAX_CONTENT_PATH = 5 * 1024 * 1024,
        TEMPLATES_AUTO_RELOAD = True,
        UPLOAD_FOLDER = "static/images/"
        )

app.jinja_env.auto_reload = True

app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Flask by default doesnt accept special characters like accents, to allow them we have to reload flask app as UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')

ADMIN = ["ftorres", "rgmark", "kpierce"]
Project_Admin = ["ftorres", "rgmark", "kpierce", "alistairewj", "tpollard"]

####################################################################################################################################
def send_email(Subject, Content, sender, rec=None):
    '''
    This functions sends an email, takes subject, content, sender and recipients
    The recipients has to be a list of emails, even is there is only one
    '''
    server = SMTP('mail.ecg.mit.edu')
    msg = MIMEText(Content.decode('utf-8'), 'plain', 'utf-8')
    recipients = ['ftorres@mit.edu'] #, 'kpierce@mit.edu'] # must be a list
    if rec != None:
        recipients = rec
    msg['Subject'] = Subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()
####################################################################################################################################
def send_html_email(Subject, Content, html_Content, sender, rec=None):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    recipients = ['ftorres@mit.edu'] #, 'kpierce@mit.edu'] # must be a list
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
    part1 = MIMEText(Content.decode('utf-8'), 'plain', 'utf-8')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    server = SMTP('mail.ecg.mit.edu')
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()
####################################################################################################################################
def Checkout_form(Vars):
    '''
    Checkout form function that will be called in the submittion of the 'info/submit'
    '''
    SUBJECT = 'LCP checkout form - {0}'.format(Vars['email'] )
    Content = "\nLastname: {0}\nFirstname: {1}\nEnd date: {2}\n".format(Vars['lastname'], Vars['firstname'], Vars['enddate'])
    Content += "Archive location:\nMachine name: {0}\nFilepath: {1}\nSpecial instructions: {2}\nNew preferred e-mail address: {3}\nValid from (date): {4}\n".format(Vars['machine'], Vars['filepath'], Vars['instructions'], Vars['email'], Vars['email-when'])
    Content += "New office address: {0}\nValid from (date): {1}\nNew home address: {2}\nNew telephone number(s): {3}\nAnything else: {4}\n" % (Vars['office-address'], Vars['office-when'], Vars['home-address'], Vars['phone'], Vars['extra'])

    Result = SimpleModel().Insert_line_exit(Vars)
    send_email(Subject='LCP checkout form - {0}'.format(Vars['email']), Content=Content, sender=Vars['email'], rec=['ftorres@mit.edu', 'kpierce@mit.edu'])
    app.logger.info("Sent a email for the checkout form")
    if Result != True:
        app.logger.error("There was an error in the postgres insert of the Checkout_form\n{0}\n{1}".format(Content, str(Result)))
        send_email("There was an error in the Checkout form line insert", Result, 'noreply@lcp.mit.edu')
        return Result, False
    else:
        return Content, True
####################################################################################################################################
####################################################################################################################################
def Registration_form(Vars, request):
    '''
    Checkin form function that will be called in the submittion of the 'info/submit'
    '''
    SUBJECT = 'LCP registration form - {0}'.format(Vars['email'])
    Content = "\nFull Name: {0}\n\nStart date: {1}\nMIT username: {2}\nLCP username: {3}\n".format(Vars['firstname'] + " " + Vars['lastname'], Vars['startdate'], Vars['username'], Vars['lcp_username'])
    Content += "MIT ID number: {0}\nPreferred e-mail address: {1}\nOffice address: {2}\nHome address: {3}\nTelephone number(s): {4}\nEmergency contact: {5}\n".format(Vars['id'], Vars['email'], Vars['office-address'], Vars['home-address'], Vars['phone'], Vars['emergency-contact'])
    
    EXT = set(['gif', 'jpg', 'jpeg', 'png'])
    Picture = 'missing.jpg'
    if request.files.get("Picture"):
        f = request.files['Picture']
        Picture = secure_filename(f.filename) #
        if Picture.split('.')[-1] in EXT:  #secure_filename(f.filename)split('.')[-1].
            if path.isfile(app.config['UPLOAD_FOLDER'] + Picture):
                try:
                    remove(app.config['UPLOAD_FOLDER'] + Picture)
                except:
                    pass
            f.filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12)) + '.' +  Picture.split('.')[-1]
            Picture = secure_filename(f.filename)
            f.save(app.config['UPLOAD_FOLDER'] + secure_filename(f.filename))
        else:
            print(" -- WRONG FILE EXTENSION -- ")
            app.logger.error(" -- WRONG FILE EXTENSION -- ")

    Content += "\nCurrent project(s) in LCP: {0}\nFocus of research: {1}\nBio: {2}\nPicture:{3}\nEHS training date: {4}\nHuman studies training date: {5}\nAnything else: {6}\n".format(Vars['research'], Vars['Other'], Vars['Bio'], Picture, Vars['ehs_training'], Vars['human_studies_training'], Vars['extra'])
    Result = SimpleModel().Insert_line_reg(Vars, Picture)
    send_email(Subject='LCP registration form - {0}'.format(Vars['email']), Content=Content, sender=Vars['email'], rec=['ftorres@mit.edu', 'kpierce@mit.edu'])
    app.logger.info("Sent a email for the checkin form")
    if Result != True:
        app.logger.error("There was an error in the postgres insert of the Registration_form\n{0}\n{1}".format(Content, str(Result)))
        send_email("There was an error in the Checkin form line insert", Result, 'noreply@lcp.mit.edu')
        return Result, False
    else:
        return Content, True
####################################################################################################################################
####################################################################################################################################
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

    status, username = Personel_Model().GetUsernameByID(UID)

    Filename = username + '.' + f.filename.split('.')[-1]

    if os.path.exists(app.config['UPLOAD_FOLDER'] + Filename):
        os.remove(app.config['UPLOAD_FOLDER'] + Filename)

    image = Image.open(f)
    image = image.crop((x, y, w+x, h+y))
    image = image.resize((200, 200), Image.ANTIALIAS)
    

    image.save(app.config['UPLOAD_FOLDER'] + Filename)

    return Filename
####################################################################################################################################
####################################################################################################################################
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
        app.logger.error('Incorrect password or username: %s Error: %s' % (Username, str(result)))
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
            raise RuntimeError, "unexpected opcode"
    return ''.join(output)
####################################################################################################################################
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
####################################################################################################################################
####################################################################################################################################

@app.route("/info/submit", methods=['POST'])
def submit():#render the index page information
    Vars = {'firstname' : request.form.get('firstname', 'None'), 'lastname' : request.form.get('lastname', 'None'),  'startdate' : request.form.get('startdate', 'None'), 'username' : request.form.get('username', 'None'), 'lcp_username' : request.form.get('lcp_username', 'None'), 'id' : request.form.get('id', 'None'), 'email' : request.form.get('email', 'None'),
            'office-address' : request.form.get('office-address', 'None'), 'home-address' : request.form.get('home-address', 'None'),  'phone' : request.form.get('phone', 'None'), 
            'emergency-contact' : request.form.get('emergency-contact', 'None'), 'research' : request.form.get('research', 'None'), 'Other' : request.form.get('Other', 'None'),
            'Bio' : request.form.get('Bio', 'None').replace("'","''"),  'ehs_training' : request.form.get('ehs_training', 'None'), 'human_studies_training' : request.form.get('human_studies_training', 'None'), 
            'extra' : request.form.get('extra', 'None'), 'enddate' : request.form.get('enddate','None'), 'machine' : request.form.get('machine', 'None'), 
            'filepath' : request.form.get('filepath', 'None'), 'instructions' : request.form.get('instructions', 'None'),  'email-when' : request.form.get('email-when', 'None'),
            #'office-address' : request.form.get('office-address', 'None'), 'office-when' : request.form.get('office-when', 'None'), 'home-address' : request.form.get('home-address', 'None')}
            'office-when' : request.form.get('office-when', 'None')}

    Content = ''
    if request.form.get('Registration_form', 'None') != 'None':
        Content, valid = Registration_form(Vars, request)
    elif request.form.get('Checkout_form', 'None') != 'None':
        Content, valid = Checkout_form(Vars)
    else:
        return render_template('info/index.html')

    return render_template('info/submit.html', Content=Content.replace("\n","<br>"))

####################################################################################################################################
@app.errorhandler(404)
def page_not_found(error):
    """
    This is the page for handling pages not found, there will be a log in apache
    """
    app.logger.error("404 - Page not found - {0}".format(request.path))
    return render_template('404.html')#, 404
####################################################################################################################################
@app.errorhandler(500)
def internal_server_error(error):
    """
    This is the page for handling internal server error, there will be a log in apache and email generated
    """
    import os
    cwd = os.getcwd()
    app.logger.error(str(cwd))
    app.logger.error("500 - Internal Server Error - {0}".format(request.path))
    app.logger.error(str(error))
    tb = str(traceback.format_exc())
    Content = "Hi,\n\nThere was a internal server error on the Flask app running the LCP website.\n"
    Content += "The time of this error is: {0}\n".format(datetime.now())
    Content += "The error messege is: {0}\nError traceback:\n{1}".format(str(error.message), tb)
    send_email("Internal Server Error - Flask LCP", Content, 'noreply_error@lcp.mit.edu')
    if 'Username' in session:
        Content += "\n\nThe user tha triggered this error is: {0}\n\nThanks!".format(session['Username'])
    send_email("Internal Server Error - Flask LCP - {0}".format(request.path), Content, 'noreply_error@lcp.mit.edu')

    return render_template('500.html')#, 404
####################################################################################################################################
@app.route('/robots.txt')
def send_text_file():
    return app.send_static_file('robots.txt')
####################################################################################################################################
@app.route("/")#Index page
@app.route("/index")
@app.route("/index.html")
@app.route("/index.shtml")
def index():#render the index page information
    return render_template('index.html')
####################################################################################################################################
####################################################################################################################################
@app.route("/projects")#Index page
@app.route("/Projects")
@app.route("/Projects.html")
@app.route("/projects.html")
@app.route("/projects.shtml")
def Projects():#render the index page information
    if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
        return render_template('404.html')#, 404
        # return render_template('projects.html', Projects=[])
    projects = Project_Model().GetAllWebsite()
    return render_template('projects.html', Projects=projects)
####################################################################################################################################
####################################################################################################################################
@app.route("/publications")#Index page
@app.route("/Publications")
@app.route("/publications.html")
@app.route("/publications.shtml")
@app.route("/Publications.html")
def Publications():#render the index page information
    return render_template('publications.html')
####################################################################################################################################
####################################################################################################################################
@app.route("/rgm_publications")#Index page
@app.route("/rgm_publications.html")
def rgm_publications():#render the index page information
    return render_template('rgm_publications.html')
####################################################################################################################################
# ####################################################################################################################################
@app.route("/brp_references")#Index page
@app.route("/brp_references.html")
def brp_references():#render the index page information
    return render_template('brp_references.html')
# ####################################################################################################################################
####################################################################################################################################
@app.route("/CCI")#Index page
@app.route("/cci")
@app.route("/CCI.html")
@app.route("/cci.html")
@app.route("/cci.shtml")
def CCI():#render the index page information
    return render_template('cci.html')
####################################################################################################################################

####################################################################################################################################
@app.route("/PhysioNet")#Index page
@app.route("/Physionet")
@app.route("/physionet")
@app.route("/PhysioNet.html")
@app.route("/Physionet.html")
@app.route("/physionet.html")
@app.route("/physionet.shtml")
def Physionet():#render the index page information
    return render_template('physionet.html')
####################################################################################################################################
####################################################################################################################################
@app.route("/BRP")#Index page
@app.route("/brp")
@app.route("/BRP.html")
@app.route("/brp.html")
@app.route("/brp.shtml")
def BRP():#render the index page information
    return render_template('brp.html')
####################################################################################################################################
# 1. General
# 2. Colaborating Researcher
# 3. Visiting Colleague
# 4. Alumni
# 5. Grad Student
# 6. UROP
# 7. Affiliate
# 8. Other
####################################################################################################################################
@app.route("/people")#Index page
@app.route("/People")
@app.route("/people.html")
@app.route("/People.html")
@app.route("/people.shtml")
def people():#render the index page information
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
####################################################################################################################################
####################################################################################################################################
@app.route("/login")#Signup page
@app.route("/Login")#Signup page
@app.route("/login.html")#Signup page
@app.route("/Login.html")#Signup page
def login():
    if 'ERROR' in session:#If there is an error then display the message
        Error = session['ERROR']
        session.pop('ERROR', None)
        app.logger.error('Loggin error: %s' % Error)
        return render_template('admin/login.html', Error=Error)
    else:
        return render_template('admin/login.html')
####################################################################################################################################
####################################################################################################################################
@app.route("/Authenticate", methods=['POST','GET'])#Signup page
def Authenticate():
    if request.method == 'GET':
        return redirect('login')
    Username = re.sub(r"[!@#$%^&*()_+\[\]{}:\"?><,/\'\;~` ]", '', request.form.get('Username', None))
    if Username != None and request.form.get('Password', None) != None:
        Success = Auth(Username, request.form.get('Password', None))
        if Success:
            return redirect('dashboard')
    session["ERROR"] = "Incorrect login or password."
    return redirect('login')

####################################################################################################################################
####################################################################################################################################
@app.route("/User_List")
@app.route("/User_List.html")
def User_List():
    if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
        session['ERROR'] = "Please authenticate."
        return redirect('/login')
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
####################################################################################################################################
####################################################################################################################################
@app.route("/new_project", methods=['POST','GET'])
def manage_projects():
    if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
        session['ERROR'] = "Please authenticate."
        return redirect('/login')

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
####################################################################################################################################
####################################################################################################################################
@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard():
    if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
        session['ERROR'] = "Please authenticate."
        return redirect('login')
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
    People      = UserModel.GetAll() #Normalize_utf8(UserModel.GetAll())
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
####################################################################################################################################
####################################################################################################################################
@app.route("/Edit_Project_<id>")
def project(id):
    """
    FUNCTION to do project edits
    """
    if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
        session['ERROR'] = "Please authenticate."
        return redirect('login')

    app.logger.info('The user {0} is trying to edit a project ID {1}'.format(session['Username'], id))
    session.permanent = True

    E = S = P_Output = ''
    if 'ERROR' in session:
        E = session['ERROR']
        session.pop('ERROR', None)
    elif 'SUCCESS' in session:
        S = session['SUCCESS']
        session.pop('SUCCESS', None)
    if session['Username'] in Project_Admin:# app.config["Project_Admin"]: #
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
####################################################################################################################################
####################################################################################################################################
@app.route("/Edit_User_<id>")
def user(id):
    if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
        session['ERROR'] = "Please authenticate."
        return redirect('login')
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

####################################################################################################################################
# 1. General
# 2. Colaborating Researcher
# 3. Visiting Colleague
# 4. Alumni
# 5. Grad Student
# 6. UROP
# 7. Affiliate
# 8. Other
####################################################################################################################################
@app.route("/Submit_User", methods=['POST','GET'])#Signup page
def Submit_User():
    """
    FUNCTION to handle user edits
    """
    if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
        session['ERROR'] = "Please authenticate."
        return redirect('/login')

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
                send_html_email(Subject, Content, html_Content.replace('\n','<br>'), 'noreply@lcp.mit.edu')#, rec=['rgmark@mit.edu', 'kpierce@mit.edu', 'ftorres@mit.edu']) 
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


if __name__ == "__main__":#RUN THE APP in port 8083
    # Once the templates are edited, this is needed to refresh the HTML automaticly
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', port=8083, threaded=True)#, debug=True)
    
