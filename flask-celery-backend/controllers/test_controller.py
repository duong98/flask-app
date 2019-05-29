from tasks import set_countdown
from models.test_model import db, Uuser, Address
import datetime
from flask_sqlalchemy import SQLAlchemy
from celery.result import AsyncResult

now = datetime.datetime.now() + datetime.timedelta(seconds=30)
address = Address.query.first()
res = set_countdown(address.id, 20, 20)
# task_id = "coundown" + address.id
address.active = res.parent.get()
db.session.commit()