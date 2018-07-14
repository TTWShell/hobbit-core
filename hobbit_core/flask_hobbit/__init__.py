"""
    flask_hobbit
    ~~~~~~~~~~~~

    Common utils for flask app.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


class HobbitManager:

    def __init__(self, app=None, db=None, ma=None, **kwargs):
        """
        app: The Flask application instance.
        db: An Object-Database Mapper instance such as SQLAlchemy.
        ma: The Marshmallow instance.
        """
        self.app = app
        if app is not None:
            self.init_app(app, db, ma, **kwargs)

    def init_app(self, app, db, ma, **kwargs):
        if not isinstance(app, Flask):
            raise TypeError(
                'flask_hobbit.HobbitManager.init_app(): '
                'Parameter "app" is an instance of class "{}" '
                'instead of a subclass of class "flask.Flask".'.format(
                    app.__class__.__name__))

        if not isinstance(db, SQLAlchemy):
            raise TypeError('flask_hobbit be dependent on SQLAlchemy.')
        self.db = db

        if ma and not isinstance(ma, Marshmallow):
            raise TypeError('flask_hobbit be dependent on Marshmallow.')
        self.ma = ma

        # Bind Flask-Hobbit to app
        app.hobbit_manager = self
