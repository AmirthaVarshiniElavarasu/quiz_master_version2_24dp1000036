from flask import Flask, jsonify
from flask_cors import CORS
from application.database import db,migrate
from application.userdb import datastore
from application.config import LocalDevelopmentConfig
from flask_security import Security, hash_password
from datetime import date
from flask_restful import Api
from application.celery_init import celery_init_app
from celery.schedules import crontab
from application.tasks import monthly_report
from application.extension import cache



def create_app():

    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/2'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  

    cache.init_app(app) 
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
celery = celery_init_app(app)

celery.autodiscover_tasks()




from application.routes import *


@celery.on_after_finalize.connect 
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute = '*/1'),
        monthly_report.s(),
    )

celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'daily_reminder',
        'schedule': crontab(minute='*'),  
    },
}

register_routes(api)

if __name__ == '__main__':
    app.run(debug=True)

