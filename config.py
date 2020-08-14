# Import necessary packages
import os

# Base configuration
class Config:
    # Flask configuration
    PERMANENT_SESSION_LIFETIME = os.environ.get('PERMANENT_SESSION_LIFETIME')
    MAX_CONTENT_PATH = os.environ.get('MAX_CONTENT_PATH')
    TEMPLATES_AUTO_RELOAD = os.environ.get('TEMPLATES_AUTO_RELOAD')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

    # Django configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Google Cloud configuration
    SERVICE_ACCOUNT_EMAIL = os.environ.get('SERVICE_ACCOUNT_EMAIL')
    SERVICE_ACCOUNT_KEY = os.environ.get('SERVICE_ACCOUNT_KEY')
    GCP_SECRET_KEY = os.environ.get('GCP_SECRET_KEY')

    # Database configuration
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWD = os.environ.get('DB_PASSWD')
    DB_NAME = os.environ.get('DB_NAME')
    DB_PORT = os.environ.get('DB_PORT')
    DB_HOST = os.environ.get('DB_HOST')

    # Admin configuration
    ADMIN = os.environ.get('ADMIN')
    EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS')
    PRIMARY_ADMIN = os.environ.get('PRIMARY_ADMIN')
    GCP_DELEGATION_EMAIL = os.environ.get('GCP_DELEGATION_EMAIL')
    DATATHON_GROUP = os.environ.get('DATATHON_GROUP')

# Config used for development
class DevConfig(Config):
    DEBUG = True
    TESTING = True

# Config used for production
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
