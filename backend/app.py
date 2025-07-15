from flask import Flask, jsonify
from flask_cors import CORS
from application.database import db
from application.models import User, Role
from application.config import LocalDevelopmentConfig
from flask_security import Security, SQLAlchemyUserDatastore
from datetime import date
from flask_security import hash_password


def create_app():

    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app,datastore)
    app.app_context().push()
    return app

app= create_app()
CORS(app)    

@app.route('/api/hello')
def Hello():
    return jsonify(message="Hello from Flask")

def setup_database():
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
    
with app.app_context():
    setup_database()

if __name__ == '__main__':
    app.run(debug=True)

