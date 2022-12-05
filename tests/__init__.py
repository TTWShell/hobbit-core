import os
import shutil
import functools

from flask_sqlalchemy import model

from .test_app.run import app, db


class BaseTest(object):
    root_path = os.path.split(os.path.abspath(__name__))[0]

    @classmethod
    def setup_class(cls):
        with app.app_context():
            db.create_all(bind_key=None)
            db.create_all(bind_key='mysql')

    @classmethod
    def teardown_class(cls):
        with app.app_context():
            db.drop_all(bind_key=None)
            db.drop_all(bind_key='mysql')

    def teardown_method(self, method):
        with app.app_context():
            for m in [m for m in db.Model.registry._class_registry.values()
                      if isinstance(m, model.DefaultMeta) and
                      getattr(m, '__bind_key__', None) != 'oracle']:
                db.session.query(m).delete()
                db.session.commit()


def rmdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def chdir(path):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            cwd = os.getcwd()
            if not os.path.exists(path):
                os.makedirs(path)
            os.chdir(path)
            func(*args, **kwargs)
            os.chdir(cwd)
        return inner
    return wrapper
