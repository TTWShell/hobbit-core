import os
import shutil


class BaseTest:

    def setup_method(self, method):
        print('\n{}::{}'.format(type(self).__name__, method.__name__))


def rmdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
