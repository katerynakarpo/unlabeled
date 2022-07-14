from flask import request, Response, abort
import requests


def init_views(app, **kwargs):
    users_auth_url = kwargs['users_auth_url']
    users_url = kwargs['users_utl']
    books_url = kwargs['books_url']

    @app.route('/', methods=['GET'])
    def health_checker():
        return 'Gateway work fine.'

    @app.route('/registration/', methods=['POST'])
    def signup():
        json_fields = ['first_name', 'last_name', 'email', 'password']
        data = request.json
        for j_f in json_fields:
            if j_f not in data:
                return {'error': f"json doesn`t exists {j_f}"}, 400

        res = requests.post(users_auth_url + '/registration', json=data)
        return res.json(), res.status_code

    @app.route('/login', methode=['POST'])
    async def login():
        json_fields = ['email', 'password']
        data = request.json
        for j_f in json_fields:
            if j_f not in data:
                return {'error': f"json doesn`t exists {j_f}"}, 400

        res = requests.post(users_auth_url + '/login', json=data)
        return res.json(), res.status_code
