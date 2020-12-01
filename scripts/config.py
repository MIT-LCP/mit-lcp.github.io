# Import necessary packages
import os
import ast

from dotenv import load_dotenv

load_dotenv()


# Base configuration
class Config:
    # Flask configuration
    TEMPLATES_AUTO_RELOAD = os.environ.get('TEMPLATES_AUTO_RELOAD')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    ENV = os.environ.get('FLASK_ENV')

    # Django configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database configuration
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWD = os.environ.get('DB_PASSWD')
    DB_NAME = os.environ.get('DB_NAME')
    DB_PORT = os.environ.get('DB_PORT')
    DB_HOST = os.environ.get('DB_HOST')

    # Admin configuration
    ADMIN = os.environ.get('ADMIN')
    EMAIL_RECIPIENTS = ast.literal_eval(os.environ.get('EMAIL_RECIPIENTS'))
    PRIMARY_ADMIN = ast.literal_eval(os.environ.get('PRIMARY_ADMIN'))


# Config used for development
class DevConfig(Config):
    DEBUG = True
    TESTING = True


# Config used for production
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
