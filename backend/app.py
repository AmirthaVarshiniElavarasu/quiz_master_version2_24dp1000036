from flask import Flask, jsonify
from flask_cors import CORS
from application.database import db
from application.models import User, Role
from application.config import LocalDevelopmentConfig
from flask_security import Security, SQLAlchemySessionUserDatastore


def create_app():

    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    datastore = SQLAlchemySessionUserDatastore(db, User, Role)
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
    
with app.app_context():
    setup_database()

if __name__ == '__main__':
    app.run(debug=True)

