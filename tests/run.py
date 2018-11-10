import os
from flask import Flask

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


def init_app(config=ConfigClass):
    app = Flask(__name__)
    app.config.from_object(config)

    register_extensions(app)
    register_blueprints(app)

    return app


app = init_app()
