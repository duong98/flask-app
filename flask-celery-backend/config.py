DB_USER = 'root'
DB_PASSWORD = 'TungDuong@1998'
DB_HOST = 'localhost'
DB_DB = 'mydb'
JWT_SECRET = "my secret_key"
DEBUG = True
PORT = 3306
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + '/' + DB_DB
SQLALCHEMY_TRACK_MODIFICATIONS = False
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_IMPORTS = ('tasks')
REDIS_HOST = 'localhost'
REDIS_PASSWORD = ''
REDIS_PORT = 6379
REDIS_URL = 'redis://localhost:6379'
admin = {
    'id': 1,

    'username': 'admin',

    'password': '123456'
}
import hashlib
import binascii
import os
def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
admin['password'] = hash_password(admin['password'])
