import os
import sys
sys.path.append(os.getcwd())
import re
import secrets
# from dataclasses import dataclass
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def check_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return True
    else:
        return False


def check_password(password):
    pswd_warning = []
    if len(password) < 8:
        pswd_warning.append("Make sure your password is at lest 8 letters")
    if re.search('[0-9]', password) is None:
        pswd_warning.append("Make sure your password has a number in it")
    if re.search('[A-Z]', password) is None:
        pswd_warning.append("Make sure your password has a capital letter in it")
    if re.search('[a-z]', password) is None:
        pswd_warning.append("Make sure your password has a lower letter in it")

    if not pswd_warning:
        return True, pswd_warning
    else:
        return False, pswd_warning



class Users(db.Model):
    __tablename__ = 'users'

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

    def get_info(self, params: list = None):
        return {k: self.__dict__[k] for k in params} if params else self.__dict__


class LoginSessions(db.Model):
    __tablename__ = 'login_sessions'

    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    token = db.Column(db.String(140))
    device_name = db.Column(db.String(200))

    def __init__(self, user_id, is_active, token, device_name):
        self.user_id = user_id
        self.is_active = is_active
        self.token = token
        self.device_name = device_name


class Rating(db.Model):
    __tablename__ = 'user_rating'
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    rating_value = db.Column(db.Integer, default=0)

    def __init__(self, user_id, rating_value=0):
        self.user_id = user_id
        self.rating_value = rating_value


def update_rating(user_id, rating_val_upd):
    db.session.query(Rating).filter(Rating.user_id == user_id).update({'rating_value': rating_val_upd})
    db.session.commit()


def get_rating(user_id):
    rating_val = db.session.query(Rating.rating_value).filter(Rating.user_id == user_id).first()
    return rating_val[0]


# registration functions
def create_user(data: dict):
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    password = data['password']
    if not check_email(email):
        raise ValueError("invalid email")
    valid_pswd, pswd_warning = check_password(password)
    if not valid_pswd:
        raise ValueError("Invalid password:\n"+',\n'.join(pswd_warning))
    user = Users(first_name, last_name, email, password)
    # Actually add this user to the database
    db.session.add(user)
    # Save all pending changes to the database
    db.session.commit()
    return user, user.user_id


def user_rating_setup(user_id):
    user_rating = Rating(user_id)
    db.session.add(user_rating)
    db.session.commit()


#  login functions

def get_user_id_by_email(email):
    user_id = db.session.query(Users.user_id).filter(Users.email == email).first()
    return user_id


def is_valid_pswrd_by_email(email, password):
    password_hash = db.session.query(Users.password_hash).filter(Users.email == email).first()
    checker = Users.check_password(password_hash, password)
    return checker


def generate_token(user_id, device_name):
    token = secrets.token_hex(16)
    login_session = LoginSessions(user_id, is_active=True, token=token, device_name=device_name)
    db.session.add(login_session)
    # Save all pending changes to the database
    db.session.commit()
    return token


def if_exists_device_name_by_user(device_name, user_id):
    exists = db.session.query(LoginSessions.token).filter(
        (user_id == user_id) & (device_name == device_name)).first() is not None
    return exists


# TODO: delete token after logout
def get_token(data: dict):
    email = data['email']
    password = data['password']
    device_name = data['device_name']
    user_exists = get_user_id_by_email(email) is not None

    if user_exists:
        user_id = get_user_id_by_email(email)[0]
        if is_valid_pswrd_by_email(email, password):
            if if_exists_device_name_by_user(device_name,user_id):
                token = db.session.query(LoginSessions.token).filter(
                    (LoginSessions.user_id == user_id) & (LoginSessions.device_name == device_name)).first()

                # update here flag is_active
                db.session.query(LoginSessions).filter((user_id == user_id)
                                                          & (device_name == device_name)
                                                          ).update({'is_active':True})

            else:
                token = generate_token(user_id=user_id, device_name=device_name)
            return token[0]
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


def is_token_valid(token):
    exists = db.session.query(LoginSessions.user_id).filter_by(token=token).first() is not None
    return exists


# all users values
def get_all_users(fields=None):
    if fields is None:
        fields = ['first_name', 'last_name', 'email']
    # users = db.session.query(Users).options(load_only(*fields)).all()
    users = [u.get_info(fields) for u in db.session.query(Users).all()]
    return users


def update_user_info(token: str, data: dict):
    # cols = [*data]
    # vals = list(data.values())
    user_id = user_id_by_token(token)
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email'].lower()
    db.session.query(Users).filter(Users.user_id == user_id).update(
        {'first_name': first_name,
         'last_name': last_name,
         'email': email}
    )
    db.session.commit()
