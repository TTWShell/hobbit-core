import os
from flask import Flask

from hobbit_core.err_handler import ErrHandler

from .exts import db, ma, hobbit
from .views import bp

ROOT_PATH = os.path.split(os.path.abspath(__file__))[0]


class ConfigClass(object):
    SECRET_KEY = 'test secret key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/hobbit_core'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    TESTING = True


def register_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    hobbit.init_app(app)


def register_blueprints(app):
    app.register_blueprint(bp)


def register_error_handler(app):
    app.register_error_handler(Exception, ErrHandler.handler)


def init_app(config=ConfigClass):
    app = Flask(__name__)
    app.config.from_object(config)

    register_extensions(app)
    register_blueprints(app)
    register_error_handler(app)

    return app


app = init_app()
