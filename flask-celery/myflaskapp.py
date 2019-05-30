from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
"""class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True"""
app = Flask(__name__, static_url_path="", static_folder="templates/static")
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
celery = make_celery(app)