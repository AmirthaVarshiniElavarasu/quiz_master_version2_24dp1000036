import os

class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    #configuration
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    DEBUG = True

    #configuration for security
    SECRET_KEY = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw') # hash user credencials in session
    SECURITY_PASSWORD_HASH = "bcrypt" #mechanism for hashing password
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634') # helps to hash password
    WTF_CSRF_ENABLE = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER="Authentication"
