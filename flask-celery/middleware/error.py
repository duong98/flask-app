# make Python do floating-point division by default
from __future__ import division
# make string literals be Unicode strings
from __future__ import unicode_literals

class DecodeError(Exception):
    pass
class Error(Exception):
    pass
class APIRequestException(Exception):
    pass
class LenUserError(Error):
    pass
class LenEmailError(Error):
    pass
class LenPassError(Error):
    pass
class ExistError1(Error):
    pass
class ExistError2(Error):
    pass
class LimitError(Error):
    pass
class BadValueError(Error):
    pass
class InsufficientBidsException(Exception):
    '''
    This exception is thrown if an attempt is made to use bids from an
    autobidder with no remaining bids, a user with no bids manually tries
    to place a bid, or a user tries to create an autobidder with more bids
    than they have.
    '''
    
    def __init__(self, user, requested_number_of_bids, autobidder=None):
        '''
        Initialize a InsufficientBidsException. Takes the affected user's
        model object and the number of bids they tried to use as required
        parameters. If this exception was caused by an autobidder running
        out of bids, the autobidder can be attached as the second
        parameter.
        '''
        
        if autobidder:
            Exception.__init__(self, "There are no bids remaining in this autobidder to use up.")
        else:
            Exception.__init__(self, "User {user_name} tried to use {requested} bids but only has {actual} in his or her account.".format(user_name=user.username, requested=requested_number_of_bids, actual=user.bid_count))
        self.user = user
        self.requested_number_of_bids = requested_number_of_bids
        self.autobidder = autobidder
