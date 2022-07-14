from flask import Flask
from servers_setup import *
import socket
from threading import Thread
import books.__init__ as server_books
import users.users_auth.__init__ as server_users_auth
import users.users.__init__ as server_users
import os


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


host = get_ip()
SERVER_GATEWAY_PARAMETERS['host'] = host
SERVER_GATEWAY_PARAMETERS['api'] = f"http://{host}:{SERVER_GATEWAY_PARAMETERS['port']}"

SERVER_USERS_AUTH_PARAMETERS['host'] = host
SERVER_USERS_AUTH_PARAMETERS['api'] = f"http://{host}:{SERVER_USERS_AUTH_PARAMETERS['port']}"

SERVER_USERS_PARAMETERS['host'] = host
SERVER_USERS_PARAMETERS['api'] = f"http://{host}:{SERVER_USERS_PARAMETERS['port']}"

SERVER_BOOKS_PARAMETERS['host'] = host
SERVER_BOOKS_PARAMETERS['api'] = f"http://{host}:{SERVER_BOOKS_PARAMETERS['port']}"


def create_app():
    app = Flask(__name__)
    # try it on MAC OS
    # CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    # app.config.from_object(CONFIG_TYPE)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://katekarpo:123123asdA@localhost/unlabeled'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from gateway.views import init_views
    init_views(app,
               users_auth_url=SERVER_USERS_AUTH_PARAMETERS['api'],
               users_url=SERVER_USERS_PARAMETERS['api'],
               books_url=SERVER_BOOKS_PARAMETERS['api'])
    return app


application = create_app()


def run_gateway_server():
    print(f"starting gateway_server {SERVER_GATEWAY_PARAMETERS['api']}")

    application.run(host=SERVER_GATEWAY_PARAMETERS['host'],
                    port=SERVER_GATEWAY_PARAMETERS['port'],
                    debug=SERVER_GATEWAY_PARAMETERS['debug'],
                    threaded=SERVER_GATEWAY_PARAMETERS['threaded'])


def run_users_auth_server():
    print(f"starting server_auth_user {SERVER_USERS_AUTH_PARAMETERS['api']}")
    host = SERVER_USERS_AUTH_PARAMETERS['host']
    port = SERVER_USERS_AUTH_PARAMETERS['port']
    debug = int(SERVER_USERS_AUTH_PARAMETERS['debug'])
    threaded = int(SERVER_USERS_AUTH_PARAMETERS['threaded'])
    os.system(f"python ./users/users_auth/__init__.py --host={host} --port={port} -d={debug} -thr={threaded}")


def run_users_server():
    print(f"starting server_user {SERVER_USERS_PARAMETERS['api']}")
    # server_users.main(
    #     host=SERVER_USERS_PARAMETERS['host'],
    #     port=SERVER_USERS_PARAMETERS['port'],
    #     debug=SERVER_USERS_PARAMETERS['debug'],
    #     threaded=SERVER_USERS_PARAMETERS['threaded'])
    host = SERVER_USERS_PARAMETERS['host']
    port = SERVER_USERS_PARAMETERS['port']
    debug = int(SERVER_USERS_PARAMETERS['debug'])
    threaded = int(SERVER_USERS_PARAMETERS['threaded'])
    os.system(f"python users/users/__init__.py --host={host} --port={port} -d={debug} -thr={threaded}")


def run_books_server():
    print(f"starting book_server {SERVER_BOOKS_PARAMETERS['api']}")
    # server_books.main(
    #     host=SERVER_BOOKS_PARAMETERS['host'],
    #     port=SERVER_BOOKS_PARAMETERS['port'],
    #     debug=SERVER_BOOKS_PARAMETERS['debug'],
    #     threaded=SERVER_BOOKS_PARAMETERS['threaded'])
    host = SERVER_BOOKS_PARAMETERS['host']
    port = SERVER_BOOKS_PARAMETERS['port']
    debug = int(SERVER_BOOKS_PARAMETERS['debug'])
    threaded = int(SERVER_BOOKS_PARAMETERS['threaded'])
    os.system(f"python books/__init__.py --host={host} --port={port} -d={debug} -thr={threaded}")


# TODO: add here also ML_modeling server


def main():
    t1 = Thread(target=run_gateway_server)
    t2 = Thread(target=run_users_auth_server)
    t3 = Thread(target=run_users_server)
    t4 = Thread(target=run_books_server)

    t1.start()
    t2.start()
    t3.start()
    t4.start()


if __name__ == '__main__':
    main()

# TODO: understand how to make views here
