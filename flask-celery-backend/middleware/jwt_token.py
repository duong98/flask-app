import datetime
import jwt
from application.config import JWT_SECRET
def encode(account):
    iat = datetime.datetime.utcnow()
    return jwt.encode({
        'sub': account['id'],
        'iat': iat,
        'exp': iat + datetime.timedelta(days=365)
    }, JWT_SECRET).decode('utf-8')
def decode(access_token):
    try:
        token = jwt.decode(access_token, JWT_SECRET, leeway=10)
    except jwt.InvalidTokenError:
        return None
    return token
