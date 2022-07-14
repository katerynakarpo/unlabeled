from flask import Flask
import os
import sys
sys.path.append(os.getcwd())


def create_app():
    app = Flask(__name__)
    # try it on MAC OS
    # CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    # app.config.from_object(CONFIG_TYPE)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://katekarpo:123123asdA@localhost/unlabeled'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from users.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
    from users.users_auth.views import init_views
    init_views(app)
    return app


users_auth_app = create_app()


def main(host='0.0.0.0', port=5002, debug=False, threaded=False):
    users_auth_app.run(host=host, port=port, debug=debug, threaded=threaded)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', '--host', type=str, default='0.0.0.0')
    parser.add_argument('-p', '--port', type=str, default='5002')
    parser.add_argument('-d', '--debug', type=int, default=0, choices=[0, 1])
    parser.add_argument('-thr', '--threaded', type=int, default=1, choices=[0, 1])
    args = parser.parse_args()
    main(host=args.host, port=args.port, debug=bool(args.debug), threaded=bool(args.threaded))

    # main()