import re
import secrets
from dataclasses import dataclass
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


@dataclass
class Users(db.Model):
    __table_name__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.Text)

    # last_seen = db.Column(db.DateTime)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email.title().lower()
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_email(self, email):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if (re.search(regex, email)):
            return True
        else:
            return False

    def get_info(self, params: list = None):
        return {k: self.__dict__[k] for k in params} if params else self.__dict__


class LoginSessions(db.Model):
    __table_name__ = 'login_sessions'

    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    token = db.Column(db.String(140))

    def __init__(self, user_id, is_active, token):
        self.user_id = user_id
        self.is_active = is_active
        self.token = token


# registration functions
def creat_user(data: dict):
    first_name = data['fist_name']
    last_name = data['last_name']
    email = data['email']
    password = data['password']
    user = Users(first_name, last_name, email, password)
    # Actually add this user to the database
    db.session.add(user)
    # Save all pending changes to the database
    db.session.commit()
    return user


#  login functions

def get_user_id_by_email(email):
    user_id = db.session.query(Users.user_id).filter(Users.email == email).first()
    return user_id


def is_valid_pswrd_by_email(email, password):
    password_hash = db.session.query(Users.password_hash).filter(Users.email == email).first()
    checker = Users.check_password(password_hash, password)
    return checker


def generate_token(user_id):
    token = secrets.token_hex(16)
    login_session = LoginSessions(user_id, is_active=True, token=token)
    db.session.add(login_session)
    # Save all pending changes to the database
    db.session.commit()
    return token


def get_token(data: dict):
    email = data['email']
    password = data['password']
    user_exists = get_user_id_by_email(email) is not None

    if user_exists:
        user_id = get_user_id_by_email(email)
        if is_valid_pswrd_by_email(email, password):
            token_exists = db.session.query(LoginSessions.token).filter(
                (LoginSessions.user_id == user_id[0]) & (LoginSessions.is_active == True)).first() is not None
            if token_exists:
                token = db.session.query(LoginSessions.token).filter(
                    (LoginSessions.user_id == user_id[0]) & (LoginSessions.is_active == True)).first()
            else:
                token = generate_token(user_id[0])
            return token
    else:
        print('User does not exists')


def user_id_by_token(token):
    user_id = db.session.query(LoginSessions.user_id).filter(LoginSessions.token == token).first()
    return user_id[0]


# LOGOUT
def enable_token(token):
    user_session = LoginSessions.query.get(user_id_by_token(token))
    user_session.is_active = False
    db.session.commit()
    return 'Changed'


# all users values
def get_all_users(fields=None):
    if fields is None:
        fields = ['first_name', 'last_name', 'email']
    # users = db.session.query(Users).options(load_only(*fields)).all()
    users = [u.get_info(fields) for u in db.session.query(Users).all()]
    return users
