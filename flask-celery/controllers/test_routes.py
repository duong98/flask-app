from controllers.auction_controller import AuctionController
from controllers.item_controller import ItemController
from controllers.user_controller import UserController
from models.model import Item, Auction, User, Autobidder, Bidhistory
from myflaskapp import app
import config
from middleware import auth, error, jwt_token
from flask import url_for, redirect, render_template, request

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/how_to_win', methods=['GET'])
def how_to_win():
    return render_template('how_to_win.html')
@app.route('/account', methods=['GET'])
def account():
    return render_template('account.html')
@app.route('/bid_packs', methods=['GET'])
def bid_packs():
    return render_template('bid_packs.html')
@app.route('/account/auto_bidders', methods=['GET'])
def auto_bidders():
    return render_template('auto_bidders.html')
@app.route('/winners', methods=['GET'])
def winners():
    return render_template('winners.html')
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')
@app.route('/auctions', methods=['GET'])
def items():
    return render_template('auction.html')
@app.route('/account/bidding_history', methods=['GET'])
def bidding_history():
    return render_template('bidding_history.html')
