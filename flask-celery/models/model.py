from __future__ import division
from __future__ import unicode_literals

import datetime
import decimal
import logging
from myflaskapp import db
from middleware.error import InsufficientBidsException
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
from config import hash_password, verify_password
# from tasks import deactivate
# from celery import signature

class Item(db.Model):
    id = db.Column(db.String(250), primary_key=True)
    sale_id = db.Column(db.String(250), db.ForeignKey('user.id'))
    name = db.Column(db.String(250), nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.DECIMAL, nullable=False)
    product_url = db.Column(db.String(250))
    image_url = db.Column(db.String(250))
    auctions = db.relationship('Auction', backref='item', lazy='dynamic')

    def __init__(self, id, name, quantity_in_stock, base_price, product_url, image_url):
        self.id = id
        self.name = name
        self.quantity_in_stock = quantity_in_stock
        self.base_price = base_price
        self.product_url = product_url
        self.image_url = image_url

    @staticmethod
    def get_by_id(id):
        '''
        Generates a list of items whose id is contained in the {ids} list
        '''
        return Item.query.filter_by(id=id).first()

    def update_quantity(self, new_quantity):
        '''
        Update the quantity of this item in stock
        '''
        self.quantity_in_stock = new_quantity
        self.put()

    def update_price(self, new_price):
        '''
        Update the price of the item
        '''
        if new_price is None or new_price < 0:
            raise Exception(
                "Argument 'new_price' cannot be None or less than 0")
                
        self.base_price = new_price
        self.put()

    @staticmethod
    def get(name):
        return Item.query.filter_by(name=name).first()

    def add(self):
        db.session.add(self)
        return session_commit()
    
    def put():
        return session_commit()
        

class User(db.Model):
    id = db.Column(db.String(250), primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    items = db.relationship('Item', backref='owner', lazy='dynamic')
    create_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    bid_count = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(250))
    history = db.relationship('Bidhistory', backref='user', lazy='dynamic')
    auctions = db.relationship('Auction', backref='user', lazy='dynamic')
    autobidders = db.relationship('Autobidder', backref='user', lazy='dynamic')
    # implicit property 'active_autobidders' created by the Autobidder class
    # implicit property 'auctions_won' created by the Auction class
    # implicit property 'past_bids' created by the BidHistory class
    # implicit property 'available_bids' created by the BidPool class

    def __init__(self, id, first_name, last_name, username, email, bid_count, password):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.bid_count = bid_count
        self.password = password

    def get_by_id(id):
        return User.query.filter_by(id=id).first()

    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def add(self):
        db.session.add(self)
        return session_commit()

    def put(self):
        return session_commit()

    def set_password(password):
        return hash_password(password)

    def check_password(hash, password):
        return verify_password(hash, password)
    

class Auction(db.Model):
    
    ''' This class represents a single auction. '''
    id = db.Column(db.String(250), primary_key=True)
    item_id = db.Column(db.String(250), db.ForeignKey('item.id'))
    current_price = db.Column(db.DECIMAL, default=decimal.Decimal("0.00"))
    current_winner = db.Column(db.String(250), db.ForeignKey('user.id'))
    # the time at which this auction began accepting bids, NOT the time the auction was created
    start_time = db.Column(db.DateTime)
    auction_end = db.Column(db.DateTime)
    task_id = db.Column(db.String(250))
    active = db.Column(db.Boolean)
    history = db.relationship('Bidhistory', backref='auction', lazy='dynamic')
    autobidders = db.relationship('Autobidder', backref='auction', lazy='dynamic')
    # implicit property 'attached_autobidders' created by the Autobidder class
    # implicit property 'past_bids' created by the BidHistory class
    
    # sig = deactivate.s((id), countdown=10)
    # task = None

    def __init__(self, id, item_id, start_time):
        self.id = id
        self.item_id = item_id
        self.start_time = start_time
        self.auction_end = start_time
        self.active = False

    def add(self):
        db.session.add(self)
        return session_commit()

    def put(self):
        return session_commit()
    
           
class Autobidder(db.Model):
    '''
    This class models an auto bidder, which places bids on an auction
    automatically on behalf of its creator.
    '''
    id = db.Column(db.String(250), primary_key=True)
    user_id = db.Column(db.String(250), db.ForeignKey('user.id'), nullable=True)
    auction_id = db.Column(db.String(250), db.ForeignKey('auction.id'), nullable=True)
    remaining_bids = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime)
    last_bid_time = db.Column(db.DateTime)

    def __init__(self, id, user_id, auction_id, remaining_bids):
        self.id = id
        self.user_id = user_id
        self.auction = auction_id
        self.remaining_bids = remaining_bids
        self.create_time = datetime.datetime.utcnow()

    def get_by_id(id):
        return Auction.query.filter_by(id=id).first()

    def add(self):
        db.session.add(self)
        return session_commit()

    def put(self):
        return session_commit()
 

class Bidhistory(db.Model):
    '''
    This class models a record of a bid placed, either directly by a user
    clicking the bid button in the front end, or by an autobidder bidding
    on the user's behalf.
    '''
    id = db.Column(db.String(250), primary_key=True)
    transaction_time = db.Column(db.DateTime)
    auction_id = db.Column(db.String(250), db.ForeignKey('auction.id'))
    user_id = db.Column(db.String(250), db.ForeignKey('user.id'))

    def __init__(self, id, auction_id, user_id):
        self.id = id
        self.transaction_time = datetime.datetime.utcnow()
        self.auction_id = auction_id
        self.user_id = user_id

    def add(self):
        db.session.add(self)
        return session_commit()

    def put(self):
        return session_commit()

def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason
