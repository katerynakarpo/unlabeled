import os
from dotenv import load_dotenv

load_dotenv()

# Find the absolute file path to the top level project directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'postgresql://katekarpo:123123asdA@localhost/unlabeled'
    # Settings applicable to all environments
    SECRET_KEY = os.getenv('SECRET_KEY', default='A very terrible secret key.')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# class ProductionConfig(Config):
#     DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
