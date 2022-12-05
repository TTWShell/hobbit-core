import pytest
from importlib import reload
import random
import string

from hobbit_core import utils

from .test_app.exts import db
from .test_app.models import BulkModel, BulkModel2, \
    BulkModelMysql, BulkModel2Mysql

from . import BaseTest


class TestUtils(BaseTest):

    def test_params_dict(self):
        d = utils.ParamsDict({'1': 1})

        updated_d = d.update({'2': 2})
        # assert isinstance(updated_d, utils.ParamsDict)
        assert updated_d == {'1': 1, '2': 2}
        assert d == {'1': 1}

        reupdated = updated_d.update({'3': 3})
        # assert isinstance(reupdated, utils.ParamsDict)
        assert reupdated == {'1': 1, '2': 2, '3': 3}
        assert updated_d == {'1': 1, '2': 2}
        assert d == {'1': 1}

    def test_dict2object(self):
        obj = utils.dict2object({'a': 2, 'c': 3})
        assert obj.a == 2
        assert obj.c == 3

        # test setattr
        obj.a = 4
        assert obj.a == 4

        # test getattr
        with pytest.raises(AttributeError):
            obj.b

    # this func worked ok in py2 & py3, u'' is py2 test
    @pytest.mark.parametrize("filename, excepted", [
        # (u'哈哈.zip', u'哈哈.zip'),
        ('哈哈.zip', '哈哈.zip'),
        ('../../../etc/passwd', 'etc_passwd'),
        ('My cool movie.mov', 'My_cool_movie.mov'),
        ('__filename__', 'filename'),
        ('foo$&^*)bar', 'foobar'),
        # (u'i contain cool \xfcml\xe4uts.txt', 'i_contain_cool_umlauts.txt'),
        ('i contain cool \xfcml\xe4uts.txt', 'i_contain_cool_umlauts.txt'),
    ])
    def test_secure_filename(self, filename, excepted):
        assert utils.secure_filename(filename) == excepted


class TestUseKwargs(BaseTest):

    def test_use_kwargs_with_partial(self, client):
        payload = {'username': 'username', 'email': 'email'}
        resp = client.post('/use_kwargs_with_partial/', json=payload)
        assert resp.json == payload

    def test_use_kwargs_without_partial(self, client):
        payload = {'username': 'username', 'email': 'email'}
        resp = client.post('/use_kwargs_without_partial/', json=payload)
        assert resp.json == payload

    def test_use_kwargs_with_partial2(self, client):
        payload = {'username': 'username'}
        resp = client.post('/use_kwargs_with_partial/', json=payload)
        assert resp.json == payload

    # TODO 暂时忽略，flask+werkzeug的bug
    # def test_use_kwargs_without_partial2(self, client):
    #     payload = {'username': 'username'}
    #     resp = client.post('/use_kwargs_without_partial/', json=payload)
    #     print(resp)
    #     assert resp.status == 422  # marshmallow==v3.0.0rc4', maybe a bug
    #     # assert resp.json == {'username': 'username'}

    def test_use_kwargs_dictargmap_partial(self, client):
        resp = client.post('/use_kwargs_dictargmap_partial/', json={})
        assert resp.json == {'username': None}

    def test_use_kwargs_dictargmap_partial2(self, client):
        resp = client.post('/use_kwargs_dictargmap_partial/', json={
            'username': None})
        assert resp.json == {'username': None}

    def test_base_use_kwargs_dictargmap_whitout_partial(self, client):
        resp = client.post('/base_use_kwargs_dictargmap_partial/', json={})
        assert resp.json == {'username': None}

    def test_auto_trim(self, client):
        payload = {'username': '  username', 'email': ' email  '}
        resp = client.post('/use_kwargs_with_partial/', json=payload)
        assert resp.json == {'username': 'username', 'email': 'email'}


class TestImportSubs(BaseTest):

    def test_import_subs(self, app):
        with app.app_context():
            from . import importsub
            from .test_app.exts import db
            db.create_all(bind_key=None)
        all_ = getattr(importsub, '__all__')
        assert sorted(all_) == sorted([
            'A',
            'BaseModel',
            'G_VAR',
            'OtherUser',
            'PagedSchema',
            'PagedUserSchema',
            'User',
            'UserSchema',
            'FooService',
            'BarService',
            'b',
            'models',
            'others',
            'paged_user_schemas',
            'schemas',
            'services',
            'user_schemas'
        ])
        for name in all_:
            exec(f'from .importsub import {name}')

        setattr(importsub.others, '__all__', [importsub.others.A])
        msg = "Invalid object <class 'tests.importsub.others.A'> " + \
            "in __all__, must contain only strings."
        with pytest.raises(Exception, match=msg):
            reload(importsub)


class TestBulkInsertOrUpdate(BaseTest):

    @pytest.mark.parametrize('item_length', [0, 1, 2, 501])
    @pytest.mark.parametrize(
        'model_cls, updated_at_field_name', [
            (BulkModel, None),
            (BulkModel2, 'update'),
            (BulkModelMysql, None),
            (BulkModel2Mysql, 'update'),
        ])
    def test_bulk_create_or_update_on_duplicate(
            self, item_length, model_cls, updated_at_field_name):
        items = []
        for i in range(item_length):
            items.append({key: ''.join(random.choices(
                string.ascii_letters + "'" + '"', k=50)) for key in (
                    'x', 'y', 'z')})

        params = {
            'db': db, 'model_cls': model_cls, 'items': items,
        }
        if updated_at_field_name:
            params['updated_at'] = updated_at_field_name

        result = utils.bulk_create_or_update_on_duplicate(**params)
        assert result['items_count'] == item_length and \
            result['rowcount'] == item_length, result

        result = utils.bulk_create_or_update_on_duplicate(**params)
        assert result['items_count'] == item_length and result['rowcount'] \
            == item_length, result

        assert db.session.query(model_cls).count() == item_length
        db.session.commit()
