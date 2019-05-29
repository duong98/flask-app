from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
from myflaskapp import db

class Uuser(db.Model):
    id = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(25))

    def __init__(self, id, name):
        self.id = id
        self.name = name

class Address(db.Model):
    id = db.Column(db.String(25), primary_key=True)
    email = db.Column(db.String(24))
    active = db.Column(db.Integer)
    user_id = db.Column(db.String(24), db.ForeignKey('uuser.id'))
    users = db.relationship("Uuser", backref=db.backref("addresses", lazy='dynamic'))

    def __init__(self, id, email, user_id):
        self.id = id
        self.email = email
        self.user_id = user_id
        self.active = False