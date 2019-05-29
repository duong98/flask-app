import json
import random
import jwt
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from application import app, config, jwt_token, db
from application.model import Account
from application.error import Error, ExistError1, ExistError2, LenEmailError, LenPassError, LenUserError, LimitError


def num_there(s):
    return any(i.isdigit() for i in s)


def generate_id():
    return random.randint(3, 999999999)

def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        authorization = request.headers.get('Authorization').split()
        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }
        if len(authorization) != 2:
            return jsonify(invalid_msg), 401
        try:
            auth_token = authorization[1]
            resp = jwt_token.decode(auth_token)
            user = Account.query.filter_by(email=resp['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401  # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401
    return _verify
def admin_token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        authorizations = request.headers.get('Authorization')
        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }
        authorization = authorizations.split(" ")
        if len(authorization) != 2:
            return jsonify(invalid_msg), 401
        try:
            auth_token = authorization[1]
            resp = jwt_token.decode(auth_token)
            if config.admin['id'] != resp['sub']:
                raise RuntimeError('admin not found')
            return f(config.admin['id'], *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401  # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401
    return _verify

@app.route('/login', methods=['POST'])
def adminlogin():
    request_data = request.get_data()
    try:
        admin_data = json.loads(request_data)
        admin_user = admin_data['username']
        admin_pass = admin_data['password']
        if len(admin_user) == 0:
            raise LenUserError
        if len(admin_pass) == 0:
            raise LenPassError
    except LenUserError:
        return jsonify({'Message': 'Invalid username'}), 400
    except LenPassError:
        return jsonify({'Message': 'Invalid password'}), 400
    if config.admin['username'] == admin_user:
        if config.verify_password(config.admin['password'], admin_pass):
            auth_token = jwt_token.encode(config.admin)
            return jsonify({'auth_token': auth_token})
        else:
            return jsonify({'Message': 'pasword incorrect'}), 400
    else:
        return jsonify({'Message': 'username not found'}), 404


@app.route('/users/register', methods=['POST'])
def register():
    request_data = request.get_data()
    try:
        user_data = json.loads(request_data)
        user_name = user_data['name']
        user_email = user_data['email']
        user_pass = user_data['password']
        if len(user_name) < 3 or len(user_name) > 50:
            raise LenUserError
        if len(user_email) < 3 or len(user_email) > 255:
            raise LenEmailError
        if len(user_pass) < 5 or len(user_pass) > 10 or not num_there(user_pass) or ' ' in user_pass:
            raise LenPassError
        exist_user_email = Account.query.filter_by(email=user_email).first()
        if exist_user_email:
            raise ExistError2
    except LenUserError:
        return jsonify({'Message': 'Invalid name'}), 400
    except LenEmailError:
        return jsonify({'Message': 'Invalid email'}), 400
    except LenPassError:
        return jsonify({'Message': 'Invalid password'}), 400
    except ExistError2:
        return jsonify({'Message': 'Email existed'}), 400
    user_pass = Account.set_password(Account, user_pass)
    lastUserRecord = Account.query.filter(Account.id).all()
    newRecordId = generate_id()
    while newRecordId in lastUserRecord:
        newRecordId = generate_id()
    user = Account(id=newRecordId, email=user_email, name=user_name,
                   password=user_pass, state="inactive", typea="teacher")
    # Account.add(Account, user)
    db.session.add(user)
    db.session.commit()

    userInfo = Account.get(Account, user.id)
    if userInfo:
        returnUser = {
            'id': userInfo.id,
            'name': userInfo.name,
            'email': userInfo.email,
        }
        return jsonify(returnUser)
    else:
        return jsonify({'Message': 'user not found'}), 404


@app.route('/users/login', methods=['POST'])
def userlogin():
    request_data = request.get_data()
    try:
        data = json.loads(request_data)
        user = data['email']
        password = data['password']
        if len(user) < 3 or len(user) > 50:
            raise LenUserError
        if len(password) < 5 or len(password) > 10:
            raise LenPassError
    except LenUserError:
        return jsonify({'Message': 'Invalid email'}), 400
    except LenPassError:
        return jsonify({'Message': 'Invalid password'}), 400
    user = Account.query.filter_by(email=user).first()
    if user:
        if Account.check_password(Account, user.password, password):
            user.state = "active"
            Account.update(Account)
            user_log = {
                'id': user.id,
                'email': user.email,
                'password': user.password
            }
            auth_token = jwt_token.encode(user_log)
            return jsonify({'auth_token': auth_token})
        else:
            return jsonify({'Message': 'pasword incorrect'}), 400
    else:
        return jsonify({'Message': 'email not found'}), 404
