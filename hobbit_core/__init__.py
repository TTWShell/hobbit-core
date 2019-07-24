"""
    hobbit_core
    ~~~~~~~~~~~~

    Common utils for flask app.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class HobbitManager:
    """Customizable utils management.
    """

    def __init__(self, app=None, db=None, **kwargs):
        """
        app: The Flask application instance.
        """
        self.app = app
        if app is not None:
            self.init_app(app, db, **kwargs)

    def init_app(self, app, db, **kwargs):
        """
        app: The Flask application instance.
        """
        if not isinstance(app, Flask):
            raise TypeError(
                'hobbit_core.HobbitManager.init_app(): '
                'Parameter "app" is an instance of class "{}" '
                'instead of a subclass of class "flask.Flask".'.format(
                    app.__class__.__name__))

        if not isinstance(db, SQLAlchemy):
            raise TypeError('hobbit-core be dependent on SQLAlchemy.')
        self.db = db

        app.config.setdefault('HOBBIT_UPPER_SEQUENCE_NAME', False)

        # Bind hobbit-core to app
        app.hobbit_manager = self
