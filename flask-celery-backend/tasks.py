import datetime
from myflaskapp import celery
from models.model import Auction
from controllers.auction_controller import AuctionController
from celery import chain
from celery.result import AsyncResult

def set_countdown(id, delay):
    return chain(set_active.si(id).set(eta=delay), deactivate.si(id).set(countdown=10))()
@celery.task()
def set_active(id):
    '''
    Called when an auction first becomes active, and when the end time for an auction is reached,
    and then takes actions to maintain the state of the auction properly.
    '''
    # if this is the first heartbeat, take care of activating the auction
    auction = Auction.query.filter_by(id=id).first()
    auction.active = True
    auction.add()

@celery.task(bind=True)
def deactivate(self, id):
    auction = Auction.query.filter_by(id=id).first()
    if not AuctionController.invoke_autobidders(auction):
        AuctionController.close_auction(auction)
    else:
        self.apply_async((id), countdown=10)

@celery.task
def add(a, b):
    return a + b