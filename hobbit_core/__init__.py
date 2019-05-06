"""
    hobbit_core
    ~~~~~~~~~~~~

    Common utils for flask app.
"""

from flask import Flask


class HobbitManager(object):
    """Customizable utils management.
    """

    def __init__(self, app=None, **kwargs):
        """
        app: The Flask application instance.
        """
        self.app = app
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """
        app: The Flask application instance.
        """
        if not isinstance(app, Flask):
            raise TypeError(
                'hobbit_core.HobbitManager.init_app(): '
                'Parameter "app" is an instance of class "{}" '
                'instead of a subclass of class "flask.Flask".'.format(
                    app.__class__.__name__))

        # Bind Flask-Hobbit to app
        app.hobbit_manager = self
