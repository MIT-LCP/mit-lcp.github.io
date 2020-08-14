#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from sys import stderr as http_logger

import psycopg2

from config import Config


class BaseModel:
    """
    Initial connection to dabase
    """
    def __init__(self):
        try:
            self.con = psycopg2.connect("dbname={0} user={1} host={2} \
                password={3}".format(Config.DB_NAME, Config.DB_USER,
                                     Config.DB_HOST, Config.DB_PASSWD))
            self.cur = self.con.cursor()
        except psycopg2.Error as error:
            http_logger.write("Error connecting: {0}".format(error))

    def __del__(self):
        try:
            self.con.close()
        except psycopg2.Error as error:
            http_logger.write("Error connecting: {0}".format(error))


class PersonelModel(BaseModel):
    """
    Handle everything that has to do with LCP people
    """
    def new_person(self, name, status, pic, email, bio):
        """
        Add a new person to the LCP website
        """
        try:
            self.cur.execute("""INSERT INTO "Lab"."Personel" ("Full_Name",
                "Status", "Email", "Bio", "Picture") VALUES ('%s', '%s',
                '%s', '%s', '%s')""" % (name, status, email, bio, pic))
            self.con.commit()
            return 1
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.new_person: \
                {}".format(error))
            raise Exception(error)

    def update(self, name, status, pic, email, bio, uid, food, hidden):
        """
        Update a person's LCP websites profile
        """
        try:
            self.cur.execute("""UPDATE "Lab"."Personel" SET ("Full_Name",
                "Status", "Email", "Bio", "Picture", "Food", "Hidden") = (
                '%s', '%s', '%s', '%s', '%s', '%s', '%s') WHERE "UID"=%s""" % (
                    name, status, email, bio, pic, food, hidden, uid))
            self.con.commit()
            return 1
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.update: \
                {}".format(error))
            raise Exception(error)

    def get_picture(self, uid):
        """
        Get the picture name from the user ID
        """
        try:
            self.cur.execute("""SELECT "UID", "Picture" FROM "Lab"."Personel"
                WHERE "UID"='%s' """ % (uid))
            return self.cur.fetchone()
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.get_picture function: \
                {}".format(error))
            raise Exception(error)

    def get_all(self):
        """
        Get all users
        """
        try:
            self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status",
                "Picture", "Title", "Email", "Date", "Username", "Food",
                "Hidden" FROM "Lab"."Personel" ORDER BY "Status","UID" ASC """)
            return self.cur.fetchall()
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.get_all function: \
                {0}".format(error))
            raise Exception(error)

    def get_all_from_id(self, uid):
        """
        Get all the user info from the ID
        """
        try:
            self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status",
                "Picture", "Title", "Email", "Date", "Username", "Food",
                "Hidden" FROM "Lab"."Personel" WHERE "UID" =%s """ % uid)
            return list(self.cur.fetchone())
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.get_all_from_id \
                function: {0}".format(error))
            raise Exception(error)

    def get_username_from_id(self, uid):
        """
        Get all the user info from the username
        """
        try:
            self.cur.execute("""SELECT "Username" FROM "Lab"."Personel"
                WHERE "UID" =%s """ % str(uid))
            return list(self.cur.fetchone())[0]
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.get_username_from_id \
                function: {0}".format(error))
            raise Exception(error)

    def get_bio_from_id(self, uid):
        """
        Get the user bio from the ID
        """
        try:
            self.cur.execute("""SELECT "Bio" FROM "Lab"."Personel" WHERE
                "UID" =%s """ % str(uid))
            return list(self.cur.fetchone())[0]
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.get_bio_from_id \
                function: {0}".format(error))
            raise Exception(error)

    def get_user_public(self):
        """
        Get all users to be shown in the website
        """
        try:
            self.cur.execute("""SELECT "UID", "Bio", "Full_Name", "Status",
                "Picture", "Title", "Email", "Date", "Username", "Food",
                "Hidden" FROM "Lab"."Personel" WHERE "Status" = 1 OR
                "Status" = 2 OR "Status" = 3 OR "Status" = 5 OR "Status" = 7
                ORDER BY "UID" ASC """)
            return self.cur.fetchall()
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.get_user_public \
                function: {0}".format(error))
            raise Exception(error)

    def registration_form(self, Vars, Picture):
        """
        KP's Registration form
        """
        try:
            self.cur.execute("""INSERT INTO "Lab"."Personel" ("Full_Name",
                "startdate", "username", "Username", "id", "Email",
                "office-address", "home-address", "phone",
                "emergency-contact", "Other", "research", "Bio", "Picture",
                "ehs_training", "human_studies_training", "extra", "Hidden")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, 'TRUE')""", (
                    Vars["firstname"] + ' ' + Vars["lastname"],
                    Vars["startdate"], Vars["username"], Vars["lcp_username"],
                    Vars["id"], Vars["email"], Vars["office-address"],
                    Vars["home-address"], Vars["phone"],
                    Vars["emergency-contact"], Vars["Other"], Vars["research"],
                    Vars["Bio"], Picture, Vars["ehs_training"],
                    Vars["human_studies_training"], Vars["extra"]))
            self.con.commit()
            return True
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.registration_form \
                function: {0}".format(error))
            raise Exception(error)

    def checkout_form(self, Vars):
        """
        KP's sign out form
        """
        try:
            self.cur.execute("""UPDATE "Lab"."Personel" SET "End_Date"='%s',
                "Machine" = '%s', "Instructions" = '%s', "New_email" = '%s',
                "New_Office"='%s', "Office_start"='%s', "New_Address"='%s',
                "New_phone"='%s', "Other_leaving"='%s'  WHERE "Full_Name"
                like '%s'""" % (Vars["enddate"], Vars["machine"],
                                Vars["instructions"], Vars["email"],
                                Vars["office-address"], Vars["office-when"],
                                Vars["home-address"], Vars["phone"],
                                Vars["extra"],
                                Vars["firstname"] + ' ' + Vars["lastname"]))
            self.con.commit()
            return True
        except psycopg2.Error as error:
            http_logger.write("Error in PersonelModel.checkout_form \
                function: {0}".format(error))
            raise Exception(error)


class DatathonModel(BaseModel):
    """
    Handle GCP datathon access
    """
    def grant_bq_access(self, var):
        """
        Add GCP access
        """
        try:
            self.cur.execute("INSERT INTO \"Lab\".datathon (location, \
                contact_name, contact_email, google_group, event_date, \
                creator_user) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', \
                '{5}')".format(var["location"], var["contact_name"],
                               var["contact_email"], var["google_group"],
                               var["date"], var["user"]))
            self.con.commit()
            return True
        except psycopg2.Error as error:
            http_logger.write("Error in Datathon_Model.Grant_BQ_access \
                function: {0}".format(error))
            raise Exception(error)

    def revoke_bq_access(self, user, datathon_id):
        """
        Remove GCP access
        """
        try:
            self.cur.execute("UPDATE \"Lab\".datathon SET (revoke_date, \
                revoke_user) = ('{0}', '{1}') WHERE id={2}".format(
                    datetime.now().strftime('%Y-%m-%d'), user, datathon_id))
            self.con.commit()
            return True
        except psycopg2.Error as error:
            http_logger.write("Error in Datathon_Model.Revoke_BQ_Access \
                function: {0}".format(error))
            raise Exception(error)

    def get_by_id(self, datathon_id):
        """
        Get persons information via the ID
        """
        try:
            self.cur.execute("SELECT location, contact_name, contact_email, \
                google_group, event_date, creation_date, revoke_date, \
                creator_user, revoke_user FROM \"Lab\".datathon WHERE id={0}\
                ".format(datathon_id))
            return self.cur.fetchone()
        except psycopg2.Error as error:
            http_logger.write("Error in Datathon_Model.GetAll \
                function: {0}".format(error))
            raise Exception(error)

    def get_all(self):
        """
        Get all the datathon access om GCP
        """
        try:
            self.cur.execute("SELECT id, location, contact_name, \
                contact_email, google_group, event_date, creation_date, \
                revoke_date, creator_user, revoke_user FROM \"Lab\".datathon \
                ORDER BY event_date DESC")
            return self.cur.fetchall()
        except psycopg2.Error as error:
            http_logger.write("Error in Datathon_Model.GetAll \
                function: {0}".format(error))
            raise Exception(error)
