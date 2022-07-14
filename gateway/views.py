from flask import request, Response, abort
import requests


# TODO: exception if another fields exists (additional)
def check_json_keys(json_fields:list,data:dict):
    for j_f in json_fields:
        if j_f not in data:
            return {'error': f"json doesn`t exists {j_f}"}, 400


def init_views(app, **kwargs):
    users_auth_url = kwargs['users_auth_url']
    users_url = kwargs['users_url']
    books_url = kwargs['books_url']

    @app.route('/', methods=['GET'])
    def health_checker():
        return 'Gateway work fine.'



    @app.route('/registration/', methods=['POST'])
    def signup():
        json_fields = ['first_name', 'last_name', 'email', 'password']
        data = request.json
        json_checker_res = check_json_keys(json_fields,data)
        if json_checker_res:
            res = requests.post(users_auth_url + '/registration', json=data)
            return res.json(), res.status_code
        return json_checker_res

    @app.route('/login/', methods=['POST'])
    def login():
        json_fields = ['email', 'password', 'device_name']
        data = request.json
        json_checker_res = check_json_keys(json_fields,data)
        if json_checker_res:
            res = requests.post(users_auth_url + '/login', json=data)
            return res.json(), res.status_code
        return json_checker_res

    @app.route('/edit_profile/', methods = ['PUT'])
    def update_user_profile():
        json_fields = ['first_name', 'last_name']
        data = request.json
        check_json_keys(json_fields,data)
        res = requests.post(users_url+'/edit_profile',json=data)
        return res.json(), res.status_code

    @app.route('/rating', methods=['GET'])
    def get_user_rating():
        pass
