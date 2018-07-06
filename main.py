from flask import Flask, render_template, redirect, request, session, Session#,  escape, url_for, jsonify, Session, g
from apscheduler.schedulers.background import BackgroundScheduler
from flask_pam.token_storage import DictStorage
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
#from werkzeug import secure_filename
from datetime import timedelta, datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_pam.token import JWT
from flask_pam import Auth
from smtplib import SMTP
from uuid import uuid4
from Postgres import *
from PIL import Image
from os import path
from re import sub
import simplepam, logging, traceback, random, string, sys, re, os, difflib

# Change the logger output file and schema
logging.basicConfig(filename='/var/log/flask/lcp_website.log', level=logging.DEBUG, format='{%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

app = Flask(__name__) # Add the debug if you are running debugging mode

app.config.update(
        PERMANENT_SESSION_LIFETIME = timedelta(seconds=3000),
        SECRET_KEY = 'mf}7WwDxTm8ik}ipULrYgSWzfxutj|zDo1n(h+abvE&$aM)?O$8R>qUtE)?CyOQ)*6YwADN!IHLy+TE^K1>>1^riVxme**JBH!+N',
        MAX_CONTENT_PATH = 5 * 1024 * 1024,
        TEMPLATES_AUTO_RELOAD = True,
        UPLOAD_FOLDER = "static/images/"
        )

app.jinja_env.auto_reload = True

# Flask by default doesnt accept special characters like accents, to allow them we have to reload flask app as UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')

ADMIN = ["ftorres", "rgmark", "kpierce"]
Project_Admin = ["ftorres", "rgmark", "kperice", "alistairewj", "tpollard"]

def cron_job():
    '''
    This function verifies the times of al the projects submitted to the LCP website, and every 60 days will send a 
    recordatory email, to check if the information is up to date. This function will be executed by a background scheduler 
    or a cronjob.
    '''
    projects = Project_Model().GetAll()
    for item in projects:
        time = item[8] - date.today()
        if time.days % 60 == 0 and time.days > 1:
            Content = "Hi %s,\nThere is a project in the LCP website that has you as the contact person." % item[1]
            Content += "There have passed %s days since the project was last updated.\n\n" % time.days
            Content += "Please log in the server here: https://lcp.mit.edu/dashboard to edit the project.\n\n"
            Content += "Thanks!"
            send_email("LCP project email warning" , Content, 'noreply@lcp.mit.edu', [item[3]])

# This is a scheduler that will execute the cron_job function, The interval for every check is 14 hours
sched = BackgroundScheduler(daemon=True)
sched.add_job(cron_job,trigger='interval',seconds=50000, name='emailing_test', id='cron_sched')
sched.start()

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
    SUBJECT = 'LCP checkout form - ' + Vars['email'] 
    Content = "\nLastname: %s\nFirstname: %s\nEnd date: %s\n" % (Vars['lastname'], Vars['firstname'], Vars['enddate'])
    Content += "Archive location:\nMachine name: %s\nFilepath: %s\nSpecial instructions: %s\nNew preferred e-mail address: %s\nValid from (date): %s\n" % (Vars['machine'], Vars['filepath'], Vars['instructions'], Vars['email'], Vars['email-when'])
    Content += "New office address: %s\nValid from (date): %s\nNew home address: %s\nNew telephone number(s): %s\nAnything else: %s\n" % (Vars['office-address'], Vars['office-when'], Vars['home-address'], Vars['phone'], Vars['extra'])

    Result = SimpleModel().Insert_line_exit(Vars)
    send_email(Subject='LCP checkout form - ' + Vars['email'], Content=Content, sender=Vars['email'], rec=['ftorres@mit.edu', 'kpierce@mit.edu'])
    app.logger.info("Sent a email for the checkout form")
    if Result != True:
        file = open(app.root_path + '/Error.log','a')
        file.write(Content)
        file.close()
        send_email("There was an error in the Checkout form line insert", Result, 'noreply@lcp.mit.edu')
        app.logger.error("There was an error in the postgres function of the chekout form, the error is:\n{0}".format(Result))
        return Result, False
    else:
        return Content, True
####################################################################################################################################
####################################################################################################################################
def Registration_form(Vars, request):
    '''
    Checkin form function that will be called in the submittion of the 'info/submit'
    '''
    SUBJECT = 'LCP registration form - ' + Vars['email']
    Content = "\nFull Name: %s\n\nStart date: %s\nMIT username: %s\nLCP username: %s\n" % (Vars['firstname'] + " " + Vars['lastname'], Vars['startdate'], Vars['username'], Vars['lcp_username'])
    Content += "MIT ID number: %s\nPreferred e-mail address: %s\nOffice address: %s\nHome address: %s\nTelephone number(s): %s\nEmergency contact: %s\n" % (Vars['id'], Vars['email'], Vars['office-address'], Vars['home-address'], Vars['phone'], Vars['emergency-contact'])
    
    EXT = set(['gif', 'jpg', 'jpeg', 'png'])
    Picture = 'missing.jpg'
    if request.files.get("Picture"):
        f = request.files['Picture']
        Picture = secure_filename(f.filename)
        if secure_filename(f.filename).split('.')[-1] in EXT:
            if path.isfile(Image_Path + secure_filename(f.filename)):
                f.filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12)) + '.' + secure_filename(f.filename).split('.')[-1] 
                f.save(Image_Path + secure_filename(f.filename))
                Picture = secure_filename(f.filename)
            else:
                f.save(Image_Path + secure_filename(f.filename))
        else:
            print(" -- WRONG FILE EXTENSION -- ")
            app.logger.error(" -- WRONG FILE EXTENSION -- ")

    Content += "\nCurrent project(s) in LCP: %s\nFocus of research: %s\nBio: %s\nPicture:%s\nEHS training date: %s\nHuman studies training date: %s\nAnything else: %s\n" % (Vars['research'], Vars['Other'], Vars['Bio'], Picture, Vars['ehs_training'], Vars['human_studies_training'], Vars['extra'])
    Result = SimpleModel().Insert_line_reg(Vars, Picture)
    send_email(Subject='LCP registration form - ' + Vars['email'], Content=Content, sender=Vars['email'], rec=['ftorres@mit.edu', 'kpierce@mit.edu'])
    app.logger.info("Sent a email for the checkin form")
    if Result != True:
        file = open(app.root_path + '/Error.log','a')
        file.write(Content)
        file.write(str(Result))
        file.close()
        send_email("There was an error in the Checkin form line insert", Result, 'noreply@lcp.mit.edu')
        app.logger.error("There was an error in the postgres function of the chekin form, the error is:\n{0}".format(Result))
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
            output.append("<font color=red>^" + seqm.b[b0:b1] + "</font>")
        elif opcode == 'delete':
            output.append("<font color=blue>^" + seqm.a[a0:a1] + "</font>")
        elif opcode == 'replace':
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append("<font color=green>^" + seqm.b[b0:b1] + "</font>")
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
    Content += "The time of this error is: %s\n" % (datetime.now())
    Content += "The error messege is: %s\n" % str(error.message)
    Content += "Error traceback:\n%s" % tb
    send_email("Internal Server Error - Flask LCP", Content, 'noreply_error@lcp.mit.edu')
    if 'Username' in session:
        Content += "\n\nThe user tha triggered this error is: %s\n\nThanks!" % session['Username']
    send_email("Internal Server Error - Flask LCP", Content, 'noreply_error@lcp.mit.edu')

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
            IDs += "<li><a href='#%s'>%s</a></li>" % (item[0], item[2])
            if item[1]:
                if "\n" in item[1] and item[1] != None:
                    Bio_Array = item[1].split("\n")
                    for line in Bio_Array:
                        Bio += "<p>" + line + "</p>"
                else:
                    Bio = "<p style='margin:0 0 0 0;'>" + item[1] + "</p>"
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
    Success = Auth(Username, request.form.get('Password', None))
    if Success:
        return redirect('dashboard')
    else:
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

    app.logger.info('The user %s is trying to edit a project ID %s' % (session['Username'], id))
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
    app.logger.info('The user %s is trying to edit the profile id %s' % (session['Username'], id))
    session.permanent = True
    E = S = P_Output = ''
    if 'ERROR' in session:
        E = session['ERROR']
        session.pop('ERROR', None)
    elif 'SUCCESS' in session:
        S = session['SUCCESS']
        session.pop('SUCCESS', None)
    Person = Personel_Model().GetAllByID(id)
    ADMIN = ["ftorres", "rgmark", "kperice"]
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

    return render_template('edit.html', Error=E, Success=S, Logged_User=session['Username'], Person=Person)

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

    if 'Success' in globals() and (Success == 1 or Success == True):
        session['SUCCESS'] = "The update was successfully done."
        return redirect('dashboard')
    else:
        session['ERROR'] = "There was an error, please try again."
        return redirect('dashboard')


if __name__ == "__main__":#RUN THE APP in port 8000
    # Once the templates are edited, this is needed to refresh the HTML automaticly
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', port=8082, threaded=True)#, debug=True)
    

# auth = Auth(DictStorage, JWT, 60, 600, app) # Python method to authenticate against the system

################################################################################################
# - From this point forward, the things defined are NOT used, and have no use BUT DONT DELTE - #
# - From this point forward, the things defined are NOT used, and have no use BUT DONT DELTE - #
# - From this point forward, the things defined are NOT used, and have no use BUT DONT DELTE - #
# - From this point forward, the things defined are NOT used, and have no use BUT DONT DELTE - #
# - From this point forward, the things defined are NOT used, and have no use BUT DONT DELTE - #
################################################################################################

# from werkzeug.wsgi import DispatcherMiddleware
# from email.mime.text import MIMEText
# from datetime import datetime
# from smtplib import SMTP
# import json, ldap

# ####################################################################################################################################
# @app.route('/.well-known/acme-challenge/<token_value>')
# def letsencrpyt(token_value):
#     """
#     Function to allow ssl verification by certbot
#     """
#     with open('.well-known/acme-challenge/{}'.format(token_value)) as f:
#         answer = f.readline().strip()
#     return answer

# app.permanent_session_lifetime = timedelta(seconds=3000)
# app.secret_key = 'mf}7WwDxTm8ik}ipULrYgSWzfxutj|zDo1n(h+abvE&$aM)?O$8R>qUtE)?CyOQ)*6YwADN!IHLy+TE^K1>>1^riVxme**JBH!+N'
# app.TEMPLATES_AUTO_RELOAD = True
# Upload_locations = "lcp/static/images/"


# def resize_image(request):
#     '''
#     This function takes the 4 values of the picture to crop it.
#     All of the images will be reshapped as a 200x200 
#     '''
#     x = float(request.form.get('x', None))
#     y = float(request.form.get('y', None))
#     w = float(request.form.get('width', None))
#     h = float(request.form.get('height', None))
#     f = request.files['Image']

#     image = Image.open(f)
#     cropped_image = image.crop((x, y, w+x, h+y))
#     resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
#     resized_image.save(Upload_locations + secure_filename(f.filename))
#     return secure_filename(f.filename)

# ####################################################################################################################################
# def Normalize_utf8(Array):
#     Array = list(Array)
#     for indx, item in enumerate(Array):
#         Array[indx] = list(item)
#         for indx2, item2 in enumerate(item):
#             if item2:
#                 try:
#                     Array[indx][indx2] = item2.decode('utf-8')
#                 except:
#                     pass
#     return Array
# ####################################################################################################################################

#     @app.route("/dashboard2")
# @app.route("/Dashboard2.html")
# @app.route("/dashboard2.html")
# def Dashboard2():
#     if ('SID' not in session) or ('Username' not in session) or ('URL' not in session):
#         session['ERROR'] = "Please authenticate."
#         return redirect('login')
#     session.permanent = True
#     E = S = P_Output = ''
#     if 'ERROR' in session:
#         E = session['ERROR']
#         session.pop('ERROR', None)
#     elif 'SUCCESS' in session:
#         S = session['SUCCESS']
#         session.pop('SUCCESS', None)


#     ADMIN       = ["ftorres", "rgmark", "kperice"]
#     UserModel   = Personel_Model()
#     People      = Normalize_utf8(UserModel.GetAll())
#     Logged_User = [session['Username'], False]
#     People = Normalize_utf8(UserModel.GetAll())
#     Personel = {"General":[],'Alumni':[],"UROP":[],"Affiliate":[],"Other":[]}
#                 # 1, 2, 3, 5... 4......... 6..........7.............8
#     if session['Username'] in ADMIN:
#         Logged_User = [session['Username'], True]
# #START OF PEOPLE
#     for indx, item in enumerate(People):
#         People[indx] = list(item)
#         if item[10] == True:
#             People[indx].append("""<option value="True" selected>True</option><option value="False">False</option>""")
#             People[indx][10] = """<option value="True" selected>True</option>"""
#         else:
#             People[indx].append("""<option value="True">True</option><option value="False" selected>False</option>""")
#             People[indx][10] = """<option value="False" selected>False</option>"""
#         if item[3] == 1 or item[3] == "1":
#             People[indx].append("<option value='1' selected> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>")
#             People[indx][3] = "<option value='1'> -- General -- </option>"
#             Personel['General'].append(People[indx])
#         elif item[3] == 2 or item[3] == "2":
#             People[indx][3] = "<option value='2'> -- Collaborating Researcher -- </option>"
#             People[indx].append("<option value='1'> -- General -- </option><option value='2' selected> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>")
#             Personel['General'].append(People[indx])
#         elif item[3] == 3 or item[3] == "3":
#             People[indx][3] = "<option value='3'> -- Visiting Colleague -- </option>"
#             People[indx].append("<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3' selected> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>")
#             Personel['General'].append(People[indx])
#         elif item[3] == 4 or item[3] == "4":
#             People[indx][3] = "<option value='4'> -- Alumni -- </option>"
#             People[indx].append("<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4' selected> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>")
#             Personel['Alumni'].append(People[indx])
#         elif item[3] == 5 or item[3] == "5":
#             People[indx][3] = "<option value='5'> -- Graduate Student -- </option>"
#             People[indx].append("<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5' selected> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>")
#             Personel['General'].append(People[indx])
#         elif item[3] == 6 or item[3] == "6":
#             People[indx][3] = "<option value='6'> -- UROP -- </option>"
#             People[indx].append("<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6' selected> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>")
#             Personel['UROP'].append(People[indx])
#         elif item[3] == 7 or item[3] == "7":
#             People[indx][3] = "<option value='7'> -- Affiliate Researcher -- </option>"
#             People[indx].append("<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7' selected> -- Research Affiliate -- </option><option value='8'> -- Other -- </option>")
#             Personel['Affiliate'].append(People[indx])
#         else:
#             People[indx][3] = "<option value='8'> -- Other -- </option>"
#             People[indx].append("<option value='1'> -- General -- </option><option value='2'> -- Collaborating Researcher -- </option><option value='3'> -- Visiting Colleague -- </option><option value='4'> -- Alumni -- </option><option value='5'> -- Graduate Student -- </option><option value='6'> -- UROP -- </option><option value='7'> -- Research Affiliate -- </option><option value='8' selected> -- Other -- </option>")
#             Personel['Other'].append(People[indx])
#         P_Output += "<option value='%s'>%s</option>" % (item[0], item[2])
#     return render_template('dashboard.html', Error=E, Success=S, Users=People, Logged_User=Logged_User)

# def ldap_server():
#     import socket, random;
#     server = ['192.168.99.113', '192.168.1.164', '192.168.100.100']
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     result = -1
#     count = 0
#     while result != 0 and count < len(server):
#         count += 1
#         random_choice = random.choice(server)
#         result = sock.connect_ex((random_choice, 389))
#     if result == 0:
#        return random_choice
#     else:
#        print("ERROR, NO LDAP SERVER FOUND!!!")

# def Normalize_utf8(Array):
#     Array = list(Array)
#     for indx, item in enumerate(Array):
#         Array[indx] = list(item)
#         for indx2, item2 in enumerate(item):
#             if item2:
#                 try:
#                     Array[indx][indx2] = item2.decode('utf-8')
#                 except:
#                     pass
#     return Array

# def Normalize_dic_utf8(Dictionary):
#     for key in Dictionary.keys():
#         try:
#             Dictionary[key] = Dictionary[key].decode('utf-8')
#         except:
#             pass
#     return Dictionary

