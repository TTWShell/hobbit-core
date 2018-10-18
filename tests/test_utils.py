# -*- encoding: utf-8 -*-
import pytest

from hobbit_core.flask_hobbit import utils

from . import BaseTest, python2_only, python3_only


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

    def test_secure_filename(self):
        filenames = (
            u'哈哈.zip', '../../../etc/passwd', 'My cool movie.mov',
            '__filename__', 'foo$&^*)bar',
            u'i contain cool \xfcml\xe4uts.txt',
        )
        excepted = (
            u'哈哈.zip', 'etc_passwd', 'My_cool_movie.mov',
            'filename', 'foobar',
            'i_contain_cool_umlauts.txt',
        )
        for i, filename in enumerate(filenames):
            assert utils.secure_filename(filename) == excepted[i]

    @python2_only
    def test_secure_filename_py2(self):
        with pytest.raises(
                Exception, message="filename must be <type 'unicode'>"):
            assert utils.secure_filename(
                'i contain cool \xfcml\xe4uts.txt') == \
                'i_contain_cool_umlauts.txt'

    @python3_only
    def test_secure_filename_py3(self):
        assert utils.secure_filename(
            'i contain cool \xfcml\xe4uts.txt') == \
            'i_contain_cool_umlauts.txt'

    def test_use_kwargs(self, client):
        payload = {'username': 'username', 'email': 'email'}
        resp = client.post('/use_kwargs_with_partial/', json=payload)
        assert resp.json == payload

        resp = client.post('/use_kwargs_without_partial/', json=payload)
        assert resp.json == payload

        payload = {'username': 'username'}
        resp = client.post('/use_kwargs_with_partial/', json=payload)
        assert resp.json == payload

        resp = client.post('/use_kwargs_without_partial/', json=payload)
        assert resp.json == {'username': 'username', 'email': None}
