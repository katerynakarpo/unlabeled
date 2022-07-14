from flask import request
from users.models import enable_token, get_rating, user_id_by_token, update_user_info, get_user_info, user_rating_update


def init_view(app):
    @app.route("/", methods=['GET'])
    async def health_checker():
        return "OKAY"

    @app.route("/edit_profile", methods=['PUT'])
    async def edit_profile():
        data = request.json
        token = data.pop('token')
        update_user_info(token, data)
        return 'Updated'

    # TODO: logout should be by token (?) - url should token or user_id contain
    @app.route("/logout", methods=['POST'])
    async def logout():
        token = request.json['token']
        enable_token(token)
        return f'Logout for user with token: {token}'

    @app.route("/rating", methods=['GET'])
    async def get_user_rating():
        token = request.json['token']
        user_id = user_id_by_token(token)
        rating_val = get_rating(user_id)
        return f'{rating_val}'

    @app.route("/update_rating", methods=['PUT'])
    async def update_rating():
        token = request.json['token']
        rating_plus_val = request.json['value']
        user_id = user_id_by_token(token)
        user_rating_update(user_id,rating_plus_val)

    @app.route("/users/me", methods=['GET'])
    async def get_user_personal_info():
        user_id = request.json['user_id']
        user_info = get_user_info(user_id)
        return user_info
