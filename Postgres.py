import psycopg2
from config import *
from datetime import datetime


class LCP_Model:

    def __init__(self):
        dbinfo = Config()
        try:
            self.con = psycopg2.connect("dbname={0} user={1} host={2} password={3}".format(dbinfo.getDBName(), dbinfo.getUser(), dbinfo.getHost(), dbinfo.getPassword()))
            self.cur = self.con.cursor()
        except psycopg2.Error as e:
            print (e)
            WriteError("Error connecting", e)

    def __del__(self):
        try:
            self.con.close()
        except psycopg2.Error as e:
            WriteError("Error connecting to the user DB: ", e)
    
    def InsertRow(self, Name, Last, Role, Email, Location):
        try:
            self.cur.execute("""INSERT INTO "Lab"."Inventory" ("Name", "Last", "Role", "Email", "Location")"""+" VALUES ('%s', '%s', '%s', '%s', '%s')" % (Name, Last, Role, Email, Location))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            WriteError("Error inserting into the users Table: ", e)
            return False

    def GetAll(self):
        try:
            self.cur.execute("""SELECT "Name", "Last", "Role", "Email", "Location", "ID" FROM "Lab"."IRB" ORDER BY "ID" """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            WriteError("Error selecting from the users Table: ", e)
            return False


    def InsertRow(self,Name, Email, Computer_Name, Monitors, Authentication, HD, OS, CPU, Graphics_Card, RAM, Location, purchased, Users, MIT_Number, Time_Used):
        try:
            SQL = """INSERT INTO Inventory (Name, Email, Computer_name, Monitors, Authentication, HD, OS, CPU, GPU, RAM, Location, Year_Purchased, Users, MIT_Property, Time_Used) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (Name, Email, Computer_Name, Monitors, Authentication, HD, OS, CPU, Graphics_Card, RAM, Location, purchased, Users, MIT_Number, Time_Used)
            self.cur.execute(SQL)
            self.con.commit()
            return True
        except MySQLdb.Error as e:
            WriteError("Error inserting into the Inventory Table: ", e)
            return False
    def ShowAll(self):
        try:
            self.cur.execute("SELECT * FROM Inventory")
            return self.cur.fetchall()
        except MySQLdb.Error as e:
            WriteError("Error selecting from the Inventory Table: ", e)
            return False

def WriteError(Function, Error):
    from datetime import datetime
    f = open("Error.txt", "a")
    f.write(str(datetime.now()) + "\n")
    f.write(str(Function))
    f.write("\n")
    f.write(str(Error))
    f.write("\n----------------------------------------------\n")
    f.close()

class Personel_Model:

    def __init__(self):
        dbinfo = Config()
        try:
            self.con = psycopg2.connect("dbname={0} user={1} host={2} password={3}".format(dbinfo.getDBName(), dbinfo.getUser(), dbinfo.getHost(), dbinfo.getPassword()))
            self.cur = self.con.cursor()
        except psycopg2.Error as e:
            print (e)
            WriteError("Error connecting", e)

    def __del__(self):
        try:
            self.con.close()
        except psycopg2.Error as e:
            WriteError("Error connecting to the user DB: ", e)

    def New_ALL(self, Full_Name, Status, Picture, Email, Bio):
        try:
            self.cur.execute("""INSERT INTO "Lab"."Personel" ("Full_Name", "Status", "Email", "Bio", "Picture")"""+" VALUES ('%s', '%s', '%s', '%s', '%s')" % (Full_Name, Status, Email, Bio, Picture))
            self.con.commit()
            return 1
        except psycopg2.Error as e:
            # WriteError("Error inserting into the users Table: ", e)
            return e

    def Update_ALL(self, Full_Name, Status, Picture, Email, Bio, UID, Food, Hidden):
        try:
            self.cur.execute("""UPDATE "Lab"."Personel" SET ("Full_Name", "Status", "Email", "Bio", "Picture", "Food", "Hidden") = ('%s', '%s', '%s', '%s', '%s', '%s', '%s') WHERE "UID"=%s""" % (Full_Name, Status, Email, Bio, Picture, Food, Hidden, UID))
            self.con.commit()
            return 1
        except psycopg2.Error as e:
            print ("""UPDATE "Lab"."Personel" SET ("Full_Name", "Status", "Email", "Bio", "Picture", "Food", "Hidden") = ('%s', '%s', '%s', '%s', '%s', '%s', '%s') WHERE "UID"=%s""" % (Full_Name, Status, Email, Bio, Picture, Food, Hidden, UID))
            return e

    def GetAllUROP(self):
        try:
            self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status", "Picture", "Title", "Email", "Date", "Username", "Food", "Hidden" FROM "Lab"."Personel" WHERE "Status" = 6 ORDER BY "UID" ASC """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            WriteError("Error selecting from the users Table: ", e)
            return False

    def GetPicture(self, UID):
        try:
            # self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status", "Picture", "Title", "Email", "Date", "Username", "Food", "Hidden" FROM "Lab"."Personel" WHERE "Status" = 1 OR "Status" = 3 OR "Status" = 5  ORDER BY "UID" ASC """)
            self.cur.execute("""SELECT "UID", "Picture" FROM "Lab"."Personel" WHERE "UID"='%s' """ % (UID))
            return self.cur.fetchone()
        except psycopg2.Error as e:
            WriteError("Error selecting from the users Table: ", e)
            return False

    def GetAll(self):
        try:
            # self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status", "Picture", "Title", "Email", "Date", "Username", "Food", "Hidden" FROM "Lab"."Personel" WHERE "Status" = 1 OR "Status" = 3 OR "Status" = 5  ORDER BY "UID" ASC """)
            self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status", "Picture", "Title", "Email", "Date", "Username", "Food", "Hidden" FROM "Lab"."Personel" ORDER BY "Status", "UID" ASC """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            WriteError("Error selecting from the users Table: ", e)
            return False

    def GetAll2(self):
        try:
            self.cur.execute("""SELECT "Full_Name", "Status", "Email", "Username", "ehs_training", "human_studies_training", "Comments" FROM "Lab"."Personel" WHERE "Status" = 1 OR "Status" = 3 OR "Status" = 5 OR "Status" = 6  ORDER BY "UID" ASC """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            WriteError("Error selecting from the users Table: ", e)
            return False

    def GetAllByID(self, ID):
        try:
            self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status", "Picture", "Title", "Email", "Date", "Username", "Food", "Hidden" FROM "Lab"."Personel" WHERE "UID" =%s """ % ID)
            return list(self.cur.fetchone())
        except psycopg2.Error as e:
            WriteError("Error selecting from the users Table: ", e)
            return False

    def GetUsernameByID(self, ID):
        try:
            self.cur.execute("""SELECT "Username" FROM "Lab"."Personel" WHERE "UID" =%s """ % str(ID))
            return True, list(self.cur.fetchone())[0]
        except psycopg2.Error as e:
            return False, e

    def GetBioByID(self, ID):
        try:
            self.cur.execute("""SELECT "Bio" FROM "Lab"."Personel" WHERE "UID" =%s """ % str(ID))
            return True, list(self.cur.fetchone())[0]
        except psycopg2.Error as e:
            return False, e

    def GetNameByUsername(self, username):
        try:
            self.cur.execute("""SELECT "Full_Name" FROM "Lab"."Personel" WHERE "Username" ='%s' """ % username)
            return True, list(self.cur.fetchone())[0]
        except psycopg2.Error as e:
            return False, e


    def GetAllWeb(self):
        try:
            self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status", "Picture", "Title", "Email", "Date", "Username", "Food", "Hidden" FROM "Lab"."Personel" WHERE "Status" = 1 OR "Status" = 2 OR "Status" = 3 OR "Status" = 5 OR "Status" = 7 ORDER BY "UID" ASC """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            WriteError("Error selecting from the users Table: ", e)
            return False

class Project_Model:

    def __init__(self):
        dbinfo = Config()
        try:
            self.con = psycopg2.connect("dbname={0} user={1} host={2} password={3}".format(dbinfo.getDBName(), dbinfo.getUser(), dbinfo.getHost(), dbinfo.getPassword()))
            self.cur = self.con.cursor()
        except psycopg2.Error as e:
            print (e)
            WriteError("Error connecting", e)

    def __del__(self):
        try:
            self.con.close()
        except psycopg2.Error as e:
            WriteError("Error connecting to the user DB: ", e)
            


    def New_ALL(self, P_info):
        try:
            self.cur.execute("""INSERT INTO "Lab"."Projects" (p_name, p_desc, p_email, p_contact, submitting_user, active_p, display_p, last_update) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (P_info["p_name"], P_info["p_desc"], P_info["p_email"], P_info["p_contact"], P_info["submitting_user"], True, True, datetime.now().strftime('%Y-%m-%d'))) #P_info["active_p"], P_info["display_p"]))
            self.con.commit()
            return 1
        except psycopg2.Error as e:
            # WriteError("Error inserting into the users Table: ", e)
            return e

    def Update_ALL(self, P_info):
        try:
            self.cur.execute("""UPDATE "Lab"."Projects" SET (p_name, p_desc, p_email, p_contact, submitting_user, active_p, display_p, last_update) = ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') WHERE "PID"=%s""" % (P_info["p_name"], P_info["p_desc"], P_info["p_email"], P_info["p_contact"], P_info["submitting_user"], P_info["active_p"], P_info["display_p"], datetime.now().strftime('%Y-%m-%d'), P_info["PID"]))
            self.con.commit()
            return 1
        except psycopg2.Error as e:
            return e

    def GetAll(self):
        try:
            self.cur.execute("""SELECT "PID", p_name, p_desc, p_email, p_contact, submitting_user, active_p, display_p, last_update FROM "Lab"."Projects" ORDER BY "PID" """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            app.logger.error(e)
            WriteError("Error selecting from the users Table: ", e)
            return False

    def GetAllWebsite(self):
        try:
            self.cur.execute("""SELECT "PID", p_name, p_desc, p_email, p_contact, submitting_user, active_p, display_p, submitting_time FROM "Lab"."Projects" WHERE active_p='False' ORDER BY "PID" """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            app.logger.error(e)
            WriteError("Error selecting from the users Table: ", e)
            return False

    def GetAllByID(self, ID):
        try:
            self.cur.execute("""SELECT "PID", p_name, p_desc, p_email, p_contact, submitting_user, active_p, display_p, submitting_time FROM "Lab"."Projects" WHERE "PID" =%s """ % ID)
            return True, list(self.cur.fetchone())
        except psycopg2.Error as e:
            return False, e

class SimpleModel:
    def __init__(self):
        dbinfo = Config()
        try:
            self.con = psycopg2.connect("dbname=" + dbinfo.getDBName() + " user=" + dbinfo.getUser() + " host=" + "192.168.11.160" + " password=" + dbinfo.getPassword())
            self.cur = self.con.cursor()
        except psycopg2.Error, e:
            print ("Error %s" % e)

    def __del__(self):
        try:
            self.con.close()
        except psycopg2.Error, e:
            print ("Error %s" % e)

    def Insert_line_reg(self, Vars, Picture):
        try:
            self.cur.execute("""INSERT INTO "Lab"."Personel" ("Full_Name", "startdate", "username", "Username", "id", "Email", "office-address", "home-address", "phone", "emergency-contact", "Other", "research", "Bio", "Picture", "ehs_training", "human_studies_training", "extra", "Hidden") VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 'TRUE')""" % (Vars["firstname"] + ' ' + Vars["lastname"], Vars["startdate"], Vars["username"], Vars["lcp_username"], Vars["id"],Vars["email"],Vars["office-address"],Vars["home-address"], Vars["phone"], Vars["emergency-contact"],Vars["Other"],Vars["research"],Vars["Bio"], Picture, Vars["ehs_training"],Vars["human_studies_training"], Vars["extra"]))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            return e

    def Insert_line_exit(self, Vars):
        try:
            self.cur.execute("""UPDATE "Lab"."Personel" SET "End_Date"='%s', "Machine" = '%s', "Instructions" = '%s', "New_email" = '%s', "New_Office"='%s', "Office_start"='%s', "New_Address"='%s', "New_phone"='%s', "Other_leaving"='%s'  WHERE "Full_Name" like '%s'""" % (Vars["enddate"], Vars["machine"], Vars["instructions"], Vars["email"], Vars["office-address"],Vars["office-when"],Vars["home-address"], Vars["phone"], Vars["extra"], Vars["firstname"] + ' ' + Vars["lastname"]))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            return e



class MIMIC_Model:
    def __init__(self):
        dbinfo = Config()
        try:
            self.con = psycopg2.connect("dbname={0} user={1} host={2} password={3}".format(dbinfo.getDBName(), dbinfo.getUser(), dbinfo.getHost(), dbinfo.getPassword()))
            self.cur = self.con.cursor()
        except psycopg2.Error as e:
            WriteError("Error connecting", e)

    def __del__(self):
        try:
            self.con.close()
        except psycopg2.Error as e:
            WriteError("Error connecting", e)

    def get_all(self):
        try:
            self.cur.execute("SELECT first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info, aws_id, google_email, other_info FROM \"Lab\".mimic_approved")
            return self.cur.fetchall()
        except psycopg2.Error as e:
            WriteError("Error getting every person", e)
            return False
    def add_all_perons(self, name, last, email, mimic, eicu=None, country=None, info=None):
        try:
            if '@' not in email:
                print ("NOT EMAIL")
                return False
            if not Not_Date(country):
                print ("IS A DATE, email {0} name {1}".format(email, name))
                return False
            self.cur.execute("INSERT INTO \"Lab\".mimic_approved (first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info ) VALUES ('{0}', '{1}','{2}', '{3}','{4}', '{5}', '{6}')".format(name, last, email, country, mimic, eicu, info))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            print ("INSERT INTO \"Lab\".mimic_approved (first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info ) VALUES ('{0}', '{1}','{2}', '{3}','{4}', '{5}', '{6}')".format(name, last, email, country, mimic, eicu, info))
            WriteError("Error adding a person", e)
            return False

    def add_person(self, name, last, email, mimic, eicu=None):
        try:
            self.cur.execute("INSERT INTO \"Lab\".mimic_approved (first_name, last_name,physionet_email, mimic_approval, eicu_approval) VALUES ('{0}', '{1}','{2}', '{3}','{4}')".format(name, last, email, mimic, eicu))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            WriteError("Error adding a person", e)
            return False
    def get_total(self):
        try:
            self.cur.execute("SELECT count(*) FROM \"Lab\".mimic_approved")
            return self.cur.fetchone()[0]
        except psycopg2.Error as e:
            WriteError("Error getting total of approved users", e)
            return False
    def get_by_email(self, email):
        try:
            self.cur.execute("SELECT first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info, aws_id, google_email, other_info FROM \"Lab\".mimic_approved where physionet_email = '{0}' or google_email = '{0}'".format(email))
            return self.cur.fetchone()
        except psycopg2.Error as e:
            WriteError("Error getting user by email", e)
            return False
    def add_google_email(self, p_email, g_email):
        try:
            self.cur.execute("UPDATE \"Lab\".mimic_approved SET (google_email) = ('{0}') where physionet_email = '{1}'".format(g_email, p_email))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            WriteError("Error adding google email", e)
            return False
    def get_email(self):
        try:
            self.cur.execute("SELECT physionet_email, google_email FROM \"Lab\".mimic_approved ")
            emails = self.cur.fetchall()
            email_list = []
            for item in emails:
                for thing in item:
                    if thing != None:
                        email_list.append(thing)
            return email_list
        except psycopg2.Error as e:
            WriteError("Error getting all emails", e)
            return False

    def add_aws_id(self, p_email, aws):
        try:
            self.cur.execute("UPDATE \"Lab\".mimic_approved SET (aws_id) = ('{0}') where physionet_email = '{1}' or google_email = '{1}'".format(aws, p_email))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            print (e)
            return False

    def get_like_name(self, name):
        try:
            self.cur.execute("SELECT first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info, aws_id, google_email, other_info, id FROM \"Lab\".mimic_approved where first_name ILIKE '%{0}%'".format(name))
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print (e)
            return False

    def get_like_last(self, last):
        try:
            self.cur.execute("SELECT first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info, aws_id, google_email, other_info, id FROM \"Lab\".mimic_approved where last_name ILIKE '%{0}%'".format(last))
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print (e)
            return False

    def get_like_email(self, email):
        try:
            self.cur.execute("SELECT first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info, aws_id, google_email, other_info, id FROM \"Lab\".mimic_approved where physionet_email ILIKE '%{0}%' or google_email ILIKE '%{0}%' ".format(email))
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print (e)
            return False

    def get_by_id(self, ID):
        try:
            self.cur.execute("SELECT first_name, last_name, physionet_email, country, mimic_approval, eicu_approval, info, aws_id, google_email, other_info, id FROM \"Lab\".mimic_approved where id = {0} ".format(ID))
            return self.cur.fetchone()
        except psycopg2.Error as e:
            print (e)
            return False

    def alter_person(self, FName, LName, Email, MIMIC_A, eicu_A, AWS, GEmail, Other, UID):
        try:
            self.cur.execute("UPDATE \"Lab\".mimic_approved SET (first_name, last_name, physionet_email, mimic_approval, eicu_approval, aws_id, google_email, other_info) = ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}') where id = '{8}'".format(FName, LName, Email, MIMIC_A, eicu_A, AWS, GEmail, Other, UID))
            self.con.commit()
            return True
        except psycopg2.Error as e:
            print (e)
            return False

# Python code to remove duplicate elements 
def duplicate_email(duplicate): 
    final_list = [] 
    duplicates = []
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num)
        else:
            duplicates.append(num)
    return final_list, duplicates

def parse_eicu():
    content = open('eicuapprovals.html').read()
    content = content.split("<table>")[1].split("</table>")[0].replace('</tr>','').split('<tr>')
    eicu = []
    for item in content:
        tmp = filter(None, item.replace('</td>','').replace('\n','').split('<td>'))
        if re.match('\d*\.',tmp[0]):
            eicu.append(tmp)

def parse_mimic():
    content = open('database_access_grantees.html').read()
    content = content.split("<table>")[1].split("</table>")[0].replace('</tr>','').split('<tr>')

    MIMIC = []
    for indx, item in enumerate(content):
        tmp = filter(None, item.replace('</td>','').replace('\n','').replace('<p>','').replace('</p>','').split('<td>'))
        if tmp and re.match('\d*\.',tmp[0]):
            MIMIC.append(tmp)
    return MIMIC

def parse_tsv():
    MIMIC = []
    content = open('tsv.txt').readlines()
    for item in content:
        if item.count('\t') > 6: 
            MIMIC.append(item.replace('\n','').split('\t'))
    return MIMIC

def Not_Date(date_string):
    date_format = '%m/%d/%Y'
    try:
        date_obj = datetime.strptime(date_string, date_format)
        return False
    except:
        return True

def is_date(date_string):
    date_format = '%m/%d/%Y'
    try:
      date_obj = datetime.strptime(date_string, date_format)
      return date_string
    except:
        try:
            date_format = '%m/%d/%Y--'
            date_obj = datetime.strptime(date_string, date_format)
            return date_string.replace('--','')
        except:
            pass

def add_from_tsv():
    MIMIC = parse_tsv()
    MimicModel = MIMIC_Model()
    Added = False
    for indx,item in enumerate(MIMIC):
        if '@' in item[2]:
            if not MimicModel.get_by_email(item[2]):
                print ("Addning people")
                empty = False
                for part in item:
                    if part == '':
                        print ("ERROR")
                        empty = True
                        return False
                if not empty:
                    result = MimicModel.add_all_perons(item[0].replace("'","''"), item[1].replace("'","''"), item[2], item[5], item[6], item[4].replace("'","''"), item[7].replace("'","''"))
                    if result == False:
                        print (result)
    return True
