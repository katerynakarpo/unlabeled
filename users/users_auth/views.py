import os
import sys

sys.path.append(os.getcwd())
from flask import request
from users.models import get_token, user_rating_setup, create_user, user_id_by_token


def init_views(app):
    @app.route("/", methods=['GET'])
    async def check_health():
        return f"Server work fine!"

    @app.route("/login", methods=['POST'])
    async def login():
        data = request.json
        try:
            token = get_token(data)
        except ValueError as e:
            return {'error': str(e)}, 400
        return {'token': token}

    @app.route("/registration", methods=['POST'])
    async def registration():
        data = request.json
        try:
            _, user_id = create_user(data)
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            if "UniqueViolation" in str(e) and "duplicate key value violates unique constraint" in str(e):
                return {'error': 'User with this email exist'}, 201
            return {'error': 'server error'}, 500
        user_rating_setup(user_id)
        return f'Created user with id: {user_id} with data :{data} '

    # TODO: reset password with email

    @app.route('/get_user_id', methods = ['GET'])
    def get_user_id_by_token():
        token = request.json['token']
        user_id = user_id_by_token(token)
        return {'user_id':user_id}
