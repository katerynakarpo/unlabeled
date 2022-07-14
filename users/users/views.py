from flask import request
from users.models import enable_token, get_rating, user_id_by_token, update_user_info


def init_view(app):
    @app.route("/", methods=['GET'])
    async def health_checker():
        return "OKAY"

    @app.route("/edit_profile", methods=['PUT'])
    async def edit_profile():
        data = request.json
        token = data.pop('token')
        update_user_info(token,data)
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

