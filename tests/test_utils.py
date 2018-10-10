# -*- encoding: utf-8 -*-
import pytest

from hobbit_core.flask_hobbit import utils

from . import BaseTest, python3_only


class TestUtils(BaseTest):

    def test_dict2object(self):
        obj = utils.dict2object({'a': 2, 'c': 3})
        assert obj.a == 2
        assert obj.c == 3

        # test setattr
        obj.a = 4
        assert obj.a == 4

        # test getattr
        with pytest.raises(AttributeError):
            print(obj.b)

    @python3_only
    def test_secure_filename(self):
        filenames = (
            '哈哈.zip', '../../../etc/passwd', 'My cool movie.mov',
            '__filename__', 'foo$&^*)bar',
            'i contain cool \xfcml\xe4uts.txt',
        )
        excepted = (
            '哈哈.zip', 'etc_passwd', 'My_cool_movie.mov',
            'filename', 'foobar',
            'i_contain_cool_umlauts.txt',
        )
        for i, filename in enumerate(filenames):
            assert utils.secure_filename(filename) == excepted[i]
