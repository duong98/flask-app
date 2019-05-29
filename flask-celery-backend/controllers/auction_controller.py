# make Python do floating-point division by default
from __future__ import division
# make string literals be Unicode strings
from __future__ import unicode_literals
from tasks import set_active, deactivate, set_countdown
from celery.result import AsyncResult
from models.model import Auction, Item, User, db, Bidhistory, Autobidder
from middleware.error import InsufficientBidsException
from datetime import timedelta
import uuid
import datetime

class AuctionController():
    ''' This class manipulates auction models. '''

    def create(self, item, start_delay):
        '''
        Creates an auction using the following parameters:
        item_name: the name of the item being auctioned
        start_delay: a timedelta object giving the duration to wait before opening the auction to bidding
        (must represent a positive time duration)
        bid_pushback_time: a timedelta object giving the amount of time to be added to an active auction when a bid is placed
        (must represent a positive time duration)
        Returns the newly created auction object to allow method chaining.
        '''
        id = uuid.uuid4()
        new_auction = Auction(id=id, item=item.id, start_time=start_delay)
        new_auction.add()
        return new_auction

    def auctions_list_current(self, count=10):
        '''
        List the currently-running auctions
        '''
        auctions = Auction.query.filter_by(active=True)
        return auctions
    
    def auction_bid_history_by_user(self, auction, user):
        '''
        Returns a list of bids by the specified user on the specified
        auction. An empty list will be returned if this user has never bid
        on this auction. An Exception will be thrown if either the user or
        auction does not exist.
        '''
                
        return auction.history.filter_by(user_id=user.id).order_by(auction.history.transaction_time)
        
    def auction_recent_bids(self, auction):
        '''
        Returns a list of usernames, price, and datetimes for the last 10 bids
        '''

        return auction.history.order_by(auction.history.desc()).limit(10)
    
    def auctions_list_all(self):
        '''
        List all auctions (administrative only)
        '''
        auctions = Auction.query.all()
        return auctions
        
    def invoke_autobidders(self, auction):
        '''
        Make the next auto bidder attached to this auction place a bid.
        Returns a boolean indicating whether any bids were placed (no bids
        would be placed if either no auto bidders with remaining bids are
        attached or there simply are no attached autobidders to this
        auction).
        '''
        # ignore autobidders owned by the last bidder, if there is one
        autobidders = auction.autobidders.filter(auction.autobidders.user_id != auction.current_winner).all()
        if not autobidders:
            return False
        autobidders.sort(key=lambda this_autobidder: this_autobidder.last_bid_time if(this_autobidder.last_bid_time) else datetime.datetime(year=datetime.MINYEAR, month=1, day=1))
        
        bid_placed = False
        for next_autobidder in autobidders:
            try:
                bids_remaining = self.use_bids_auto(next_autobidder)
                self.bid(auction, next_autobidder.user)
                bid_placed = True
                next_autobidder.put()
                if bids_remaining < 1:
                    db.session.delete(auction.autobidders.filter(auction.autobidder.id == next_autobidder.id))
                    db.session.commit()
                break
            except InsufficientBidsException as exception:
                db.session.delete(auction.autobidders.filter(auction.autobidders.id == next_autobidder.id))
                db.session.commit()
        return bid_placed

    def bids(self, auction, user):
        auction.current_price += 0.01
        auction.auction_end = datetime.datetime.now() + datetime.timedelta(seconds=10)
        auction.current_winner = user.id
        id = uuid.uuid4()
        new_bid_history = Bidhistory(id=id, auction_id=auction.id, user_id=user.id)
        new_bid_history.add()
        auction.put()

    def add_bids(self, user, bids):
        user.bid_count += bids
        user.put()

    def close_auction(self, auction):
        auction.auction_end = datetime.datetime.now()
        auction.active = False
        auction.put()
        for autobidder in auction.autobidders:
            owner = User.get_by_id(autobidder.user_id)
            self.add_bids(owner, autobidder.remaining_bids)
            owner.put()
            autobidder.remaining_bids = 0
            autobidder.put()
            db.session.delete(autobidder)

    def use_bids_auto(self, autobidder):
        autobidder.last_bid_time = datetime.datetime.now()
        autobidder.remaining_bids -= 1
        autobidder.put()

    def use_bids(self, user, bids):
        user.bid_count -= bids
        user.put()

    def auction_bid(self, auction, user):
        '''
        Performs a single bid on the given auction on behalf of the specified user.
        '''
        # Perform Bid:
        self.use_bids(user, 1)
        self.bid(auction, user)
        
    def attach_autobidder(self, auction, user, bids):
        '''
        Creates a new autobidder on the specified auction on behalf of the
        specified user with the specified number of bids.
        '''
        id = uuid.uuid4()
        new_autobidder = Autobidder(id=id, user_id=user.id, auction_id=auction.id, remaining_bids=bids)
        new_autobidder.add()

    def close_autobidder(self, auction, user):
        autobidder = auction.autobidders.filter(auction.autobidders.user_id == user.id).first()
        if autobidder:
            owner = User.get_by_id(user.id)
            self.add_bids(owner, autobidder.remaining_bids)
            owner.put()
            autobidder.remaining_bids = 0
            autobidder.put()
            db.session.delete(autobidder)
        
    def get_autobidder_remaining_bids(self, auction, user):
        '''
        Returns an integer number of bids remaining in the specified user's
        autobidder attached to the specified auction. If the user has no
        autobidder, 0 will be returned.
        '''
        autobidder = auction.attached_autobidders.filter_by(user_id=user.id).first()
        if autobidder is None:
            return 0
        else:
            return autobidder.remaining_bids
