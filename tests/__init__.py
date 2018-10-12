import os
import shutil
import six
import functools

import pytest


class BaseTest(object):
    root_path = os.path.split(os.path.abspath(__name__))[0]

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
            if not os.path.exists(path):
                os.makedirs(path)
            os.chdir(path)
            func(*args, **kwargs)
            os.chdir(cwd)
        return inner
    return wrapper


python2_only = pytest.mark.skipif(not six.PY2, reason='only support Python2')
python3_only = pytest.mark.skipif(not six.PY3, reason='only support Python3')
