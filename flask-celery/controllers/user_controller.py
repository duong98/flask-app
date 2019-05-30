# make Python do floating-point division by default
from __future__ import division
# make string literals be Unicode strings
from __future__ import unicode_literals
from models.model import User
from datetime import datetime
import uuid

class UserController():
    def create(first_name, last_name, username, email, password):
        id = str(uuid.uuid4())
        new_user = User(id=id, first_name=first_name, last_name=last_name, email=email, bid_count=100, password=password)
        new_user.add()
        return new_user

    def add_bids(user, bids):
        user.bid_count += bids
        user.put()

    def use_bids(user, bids):
        user.bid_count -= bids
        user.put()