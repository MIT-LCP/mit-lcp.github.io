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

