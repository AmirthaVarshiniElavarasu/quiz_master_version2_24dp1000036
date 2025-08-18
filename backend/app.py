from flask import Flask, send_from_directory
from flask_cors import CORS
from .application.database import db,migrate
from .application.userdb import datastore
from .application.config import LocalDevelopmentConfig
from flask_security import Security, hash_password
from datetime import date
from flask_restful import Api
import os




def create_app():

    app = Flask(
        __name__,
        static_folder="../frontend/dist",  # Vue build output
        static_url_path="")
    app.config.from_object(LocalDevelopmentConfig)

   
    db.init_app(app)
    migrate.init_app(app, db)

    #flask-security setup
    app.security = Security(app,datastore)
    
    #enable CORS
    CORS(app,supports_credentials=True) 

    with app.app_context():
     setup_database(app)
    
    app.app_context().push()
    return app

def setup_database(app):
    # Create all tables
    db.create_all()
    app.security.datastore.find_or_create_role(name = "admin",description = "Super user of Application")
    app.security.datastore.find_or_create_role(name = "user",description = "General user of Application")
    db.session.commit()

    
    if not app.security.datastore.find_user(email="useradmin@email.com"):
        app.security.datastore.create_user(email="useradmin@email.com",
                                          password= hash_password('admin@1234'),
                                          username='admin',
                                          qualification='B.sc in data science',
                                          gender='Female',
                                          dob=date(2000,12,30),
                                          roles=['admin'])
        db.session.commit()


    
app= create_app()
api = Api(app)

from application.routes import *
register_routes(api)

# Serve Vue frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# Catch-all for Vue Router history mode
@app.route("/<path:path>")
def vue_router(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

if __name__ == '__main__':
    app.run(debug=True)

