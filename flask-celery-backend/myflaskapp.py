from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery, chain

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
"""
@celery.task()
def set_countdown(auction, delay, countdown):
    return chain(set_active.si(auction).set(eta=delay), countdown.si(auction).set(countdown=countdown))()
@celery.task()
def set_active(auction):
    '''
    Called when an auction first becomes active, and when the end time for an auction is reached,
    and then takes actions to maintain the state of the auction properly.
    '''
    # if this is the first heartbeat, take care of activating the auction
    auction.activate()

@celery.task()
def countdown(auction):
    if auction.active:
        auction.close()
@celery.task()
def add(a, b):
    return a + b
    """