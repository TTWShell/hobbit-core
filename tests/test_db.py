# -*- encoding: utf-8 -*-
import pytest

from hobbit_core.flask_hobbit.db import EnumExt, transaction

from . import BaseTest
from .exts import db
from .models import User


class TestEnumExt(BaseTest):

    def test_key_index(self):
        msg = u"EnumExt member must be tuple type and length equal 2."
        with pytest.raises(TypeError, match=msg):
            class ErrTypeEnum(EnumExt):
                CREATED = (0, u'新建', 'dda')

        msg = r"duplicate values found: .*, please check key or value."
        with pytest.raises(ValueError, match=msg):
            class ErrEnum(EnumExt):
                CREATED = (0, u'新建')
                FINISHED = (0, u'已完成')

    @pytest.fixture
    def TaskState(self):
        class _TaskState(EnumExt):
            CREATED = (0, u'新建')
            FINISHED = (1, u'已完成')
        return _TaskState

    def test_strict_dump(self, TaskState):
        assert 0 == TaskState.strict_dump('CREATED')
        assert u'新建' == TaskState.strict_dump('CREATED', True)

    def test_dump(self, TaskState):
        assert {'key': 0, 'value': u'新建'} == TaskState.dump('CREATED')

    def test_load(self, TaskState):
        assert 'FINISHED' == TaskState.load('FINISHED')
        assert 'FINISHED' == TaskState.load(1)
        assert 'CREATED' == TaskState.load(u'新建')
        assert TaskState.load(100) is None

    def test_to_opts(self, TaskState):
        opts = TaskState.to_opts()
        assert opts == [
            {'key': 0, 'value': u'新建'},
            {'key': 1, 'value': u'已完成'},
        ]
        opts = TaskState.to_opts(verbose=True)
        assert opts == [
            {'key': 0, 'label': 'CREATED', 'value': u'新建'},
            {'key': 1, 'label': 'FINISHED', 'value': u'已完成'},
        ]


class TestTransaction(BaseTest):

    def test_transaction_decorator(self, client):
        @transaction(db)
        def create_user(raise_exception=True):
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)
            if raise_exception:
                raise Exception('')

        with pytest.raises(Exception):
            create_user()

        assert User.query.all() == []

        create_user(raise_exception=False)
        assert User.query.first() is not None

    def test_transaction_decorator_subtransactions(self, client):
        @transaction(db)
        def create_user1():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)

        @transaction(db)
        def create_user2():
            user = User(username='test2', email='2@b.com', password='1')
            db.session.add(user)
            raise Exception('')

        @transaction(db)
        def view_func():
            create_user1()
            assert User.query.first() is not None
            create_user2()

        with pytest.raises(Exception):
            view_func()
        assert len(User.query.all()) == 0

        def view_func2():
            create_user1()
            assert User.query.first() is not None
            create_user2()

        with pytest.raises(Exception):
            view_func2()
        assert len(User.query.all()) == 0

    def test_transaction_decorator_nested(self, client):
        @transaction(db, subtransactions=False, nested=True)
        def create_user1():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)

        @transaction(db, subtransactions=False, nested=True)
        def create_user2():
            user = User(username='test2', email='2@b.com', password='1')
            db.session.add(user)
            raise Exception('')

        @transaction(db, subtransactions=False, nested=True)
        def view_func():
            create_user1()
            assert User.query.first() is not None
            create_user2()

        with pytest.raises(Exception):
            view_func()
        assert len(User.query.all()) == 0

        def view_func2():
            create_user1()
            assert User.query.first() is not None
            create_user2()

        with pytest.raises(Exception):
            view_func2()
        assert len(User.query.all()) == 1
