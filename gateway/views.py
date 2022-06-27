import json

from gateway.__init__ import application as app
from flask import request
from gateway.models import creat_user, get_token, enable_token, get_all_users


@app.route("/")
def hello_world():
    return "Hello, my name is GATEWAY! I`m working!"


@app.route("/user/login", methods=['POST'])
def login():
    data = request.json
    token = get_token(data)
    return f'User login with token: f{token}'


@app.route("/user/registration", methods=['POST'])
def registration():
    data = request.json
    creat_user(data)
    return f'Created user with data :{data}'


@app.route("/user/logout", methods=['POST'])
def logout():
    token = request.json['token']
    enable_token(token)
    return f'Logout for user with token: {token}'


@app.route("/users", methods=['GET'])
def users():
    return json.dumps(get_all_users())


@app.route("/users/edit_profile", methods=['PUT'])
def edit_info():
    pass
    # data = request.json # get only updated rows
    # token = data.pop('token')
    # res = update_info(token, data)
    # return json.dumps({'answer': res})