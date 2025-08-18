from flask_security import SQLAlchemyUserDatastore
from .database import db
from .models import User, Role

datastore=SQLAlchemyUserDatastore(db,User,Role)