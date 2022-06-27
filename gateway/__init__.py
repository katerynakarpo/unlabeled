from flask import Flask
import os
from gateway.views import *

SERVER_MAIN_PARAMETERS = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'threaded': True,
}


def create_app():
    app = Flask(__name__)
    # try it on MAC OS
    # CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    # app.config.from_object(CONFIG_TYPE)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://katekarpo:123123asdA@localhost/unlabeled'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from gateway.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


application = create_app()

if __name__ == '__main__':
    application.run()
