import os
import shutil
import functools


class BaseTest:

    def setup_method(self, method):
        print('\n{}::{}'.format(type(self).__name__, method.__name__))

    def teardown_method(self, method):
        pass


def rmdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def chdir(path):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            cwd = os.getcwd()
            os.makedirs(path, exist_ok=True)
            os.chdir(path)
            func(*args, **kwargs)
            os.chdir(cwd)
        return inner
    return wrapper
