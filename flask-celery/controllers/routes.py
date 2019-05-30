from controllers.auction_controller import AuctionController
from controllers.item_controller import ItemController
from controllers.user_controller import UserController
from models.model import Item, Auction, User, Autobidder, Bidhistory
from myflaskapp import app
import config
import json
import datetime
from tasks import set_countdown, cancel, deactivate
from middleware import error, jwt_token
from middleware.auth import token_required
from flask import url_for, redirect, render_template, request

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
    
@app.route('/register', methods=['POST'])
def register():
    request_data = request.get_data()
    try:
        user_data = json.loads(request_data)
        user_fname = user_data['first_name']
        user_lname = user_data['last_name']
        user_name = user_data['username']
        user_email = user_data['email']
        user_pass = user_data['password']
        if len(user_name) < 3 or len(user_name) > 50:
            raise error.LenUserError
        if len(user_email) < 3 or len(user_email) > 255:
            raise error.LenEmailError
        if len(user_pass) < 5 or len(user_pass) > 10 or ' ' in user_pass:
            raise error.LenPassError
        exist_user_email = User.query.filter_by(email=user_email).first()
        if exist_user_email:
            raise error.ExistError2
    except error.LenUserError:
        return json.dumps({'Message': 'Invalid name'}), 400
    except error.LenEmailError:
        return json.dumps({'Message': 'Invalid email'}), 400
    except error.LenPassError:
        return json.dumps({'Message': 'Invalid password'}), 400
    except error.ExistError2:
        return json.dumps({'Message': 'Email existed'}), 400
    user_pass = User.set_password(user_pass)
    user = UserController.create(user_fname, user_lname, user_name, user_email, user_pass)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    request_data = request.get_data()
    try:
        user_data = json.loads(request_data)
        user_email = user_data['email']
        user_pass = user_data['password']
        if len(user_email) < 3 or len(user_email) > 50:
            raise error.LenUserError
        if len(user_pass) < 5 or len(user_pass) > 10:
            raise error.LenPassError
    except error.LenUserError:
        return json.dumps({'Message': 'Invalid email'}), 400
    except error.LenPassError:
        return json.dumps({'Message': 'Invalid password'}), 400
    user = User.query.filter_by(email=user_email).first()
    if user:
        if User.check_password(user.password, user_pass):
            user_log = {
                'id': user.id,
                'email': user.email,
                'password': user.password
            }
            auth_token = jwt_token.encode(user_log)
            return json.dumps({'auth_token': auth_token})
        else:
            return json.dumps({'Message': 'password incorrect'}), 400
    else:
        return json.dumps({'Message': 'email not found'}), 404
    return redirect(url_for('/'))

@app.route('/items', methods=['POST'])
@token_required
def create_auction():
    request_data = request.get_data()
    try:
        data = json.loads(request_data)
        name = data['name']
        quantity = data['quantity']
        price = data['price']
        p_url = data['p_url']
        i_url = data['i_url']
    except Exception as e:
        return json.dumps({'Message': 'failure'}), 400
    item = ItemController.create(name, quantity, price, p_url, i_url)
    auction = AuctionController.create(item, datetime.datetime.strptime(
        'Jun 28 2018  7:40AM', '%b %d %Y %I:%M%p'))
    task = set_countdown(auction.id, 2)
    auction.task_id = task.id
    auction.put()
    return json.dumps({'Message': 'success'}), 200


@app.route('/bids', methods=['POST'])
@token_required
def auction_bid(user):
    request_data = request.get_data()
    try:
        data = json.loads(request_data)
        auction_id = data['auction_id']
        if len(auction_id) == 0:
            raise error.LenEmailError
        if not user:
            raise error.ExistError1
        auction = Auction.query.filter_by(id=auction_id).first()
        if not auction:
            raise error.ExistError2
        if not auction.active:
            raise error.LimitError
    except error.LenUserError:
        return json.dumps({'Message': 'Invalid user id'}), 400
    except error.ExistError1:
        return json.dumps({'Message': 'user not found'}), 404
    except error.ExistError2:
        return json.dumps({'Message': 'auction not found'}), 404
    except error.ExistError2:
        return json.dumps({'Message': 'auction not active'}), 400

    AuctionController.auction_bid(auction, user)
    reset = cancel.apply_async([auction.task_id])
    res = deactivate.apply_async([auction.id], countdown=10)
    auction.task_id = res.id
    auction.put()
    return json.dumps({'Message': 'success'}), 200