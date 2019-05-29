from functools import wraps
from flask import request, abort
from application.jwt_token import decode, exceptions
from application.models.user import User
from application import config
import json


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        authorization = request.headers.get("Authorization", None)
        if not authorization:
            return json.dumps({'error': 'no authorization token provied'}), 403, {'Content-type': 'application/json'}

        try:
            token = authorization.split(' ')[1]
            resp = decode(token, None, verify=False, algorithms=['HS256'])
            user = User.query.filter_by(id=resp['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except exceptions.DecodeError as identifier:
            return json.dumps({'error': 'invalid authorization token'}), 403, {'Content-type': 'application/json'}

        return f(*args, **kwargs)

    return wrap

def admin_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        authorization = request.headers.get("Authorization", None)
        if not authorization:
            return json.dumps({'error': 'no authorization token provied'}), 403, {'Content-type': 'application/json'}

        try:
            token = authorization.split(' ')[1]
            resp = decode(token, None, verify=False, algorithms=['HS256'])
            if config.admin['id'] != resp['sub']:
                raise RuntimeError('admin not found')
            return f(config.admin, *args, **kwargs)
        except exceptions.DecodeError as identifier:
            return json.dumps({'error': 'invalid authorization token'}), 403, {'Content-type': 'application/json'}

        return f(*args, **kwargs)

    return wrap
