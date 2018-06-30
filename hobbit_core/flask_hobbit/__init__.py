"""
    flask_hobbit
    ~~~~~~~~~~~~

    Common utils for flask app.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class HobbitManager:

    def __init__(self, app=None, db=None, **kwargs):
        """
        app: The Flask application instance.
        db: An Object-Database Mapper instance such as SQLAlchemy.
        """
        self.app = app
        if app is not None:
            self.init_app(app, db, **kwargs)

    def init_app(self, app, db, **kwargs):
        if not isinstance(app, Flask):
            raise TypeError(
                'flask_hobbit.HobbitManager.init_app(): '
                'Parameter "app" is an instance of class "{}" '
                'instead of a subclass of class "flask.Flask".'.format(
                    app.__class__.__name__))

        if not isinstance(db, SQLAlchemy):
            raise TypeError('flask_role be dependent on SQLAlchemy.')

        self.db = db

        # Bind Flask-Hobbit to app
        app.hobbit_manager = self
