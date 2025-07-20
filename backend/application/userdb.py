from flask_security import SQLAlchemyUserDatastore
from application.database import db
from application.models import User, Role

datastore=SQLAlchemyUserDatastore(db,User,Role)