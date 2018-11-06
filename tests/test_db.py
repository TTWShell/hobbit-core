# -*- encoding: utf-8 -*-
import time
import pytest

from hobbit_core.flask_hobbit.db import EnumExt, transaction

from . import BaseTest
from .exts import db
from .models import User


class TestSurrogatePK(BaseTest):

    def test_surrogate_pk(self, client):
        user = User(username='test1', email='1@b.com', password='1')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        db.session.remove()
        user = User.query.get(user_id)
        assert user.created_at == user.updated_at

        time.sleep(1)
        user.email = '2@b.com'
        db.session.merge(user)
        db.session.commit()

        db.session.remove()
        user = User.query.get(user_id)
        assert user.created_at < user.updated_at


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

    def test_session(self, session):
        """assert session is isolated from db.session
        """
        assert session is not db.session

        user = User(username='test1', email='1@b.com', password='1')
        db.session.add(user)
        assert User.query.first() is not None
        assert session.query(User).first() is None

        db.session.commit()
        assert User.query.first() is not None
        db.session.remove()
        assert User.query.first() is not None
        assert session.query(User).first() is not None

        User.query.delete()
        assert User.query.first() is None
        assert session.query(User).first() is not None

        db.session.commit()
        assert User.query.first() is None
        db.session.remove()
        assert User.query.first() is None
        assert session.query(User).first() is None

    def test_transaction_decorator(self, session):
        @transaction(db)
        def create_user(raise_exception=True):
            user1 = User(username='test1', email='1@b.com', password='1')
            db.session.add(user1)
            user2 = User(username='test2', email='2@b.com', password='1')
            db.session.add(user2)
            db.session.commit()
            if raise_exception:
                raise Exception('')

        # assert user1 and user2 all rollback
        with pytest.raises(Exception):
            create_user()
        assert User.query.all() == []
        assert session.query(User).all() == []

        create_user(raise_exception=False)
        assert len(User.query.all()) == 2
        assert len(session.query(User).all()) == 2

        # assert user1 and user2 all created
        User.query.delete()
        db.session.commit()
        assert User.query.all() == []
        assert session.query(User).all() == []

        with pytest.raises(Exception):
            create_user(raise_exception=False)
            assert len(User.query.all()) == 2
            create_user(raise_exception=False)
        assert len(User.query.all()) == 2
        assert len(session.query(User).all()) == 2

    def test_transaction_decorator_nested(self, session):
        @transaction(db)
        def create_user1():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)

        @transaction(db)
        def create_user2(raise_exception=True):
            user = User(username='test2', email='2@b.com', password='1')
            db.session.add(user)
            if raise_exception:
                raise Exception('')

        @transaction(db)
        def view_func(raise_exception=True):
            create_user1()
            assert User.query.first() is not None
            create_user2(raise_exception=raise_exception)

        # assert user1 and user2 all rollback
        with pytest.raises(Exception):
            view_func()
        assert len(User.query.all()) == 0
        assert len(session.query(User).all()) == 0

        # assert user1 and user2 all created
        view_func(raise_exception=False)
        assert len(User.query.all()) == 2
        assert len(session.query(User).all()) == 2

        def view_func2():
            create_user1()
            assert User.query.first() is not None
            create_user2()

        # assert user1 created and user2 rollback
        User.query.delete()
        db.session.commit()
        assert len(User.query.all()) == 0
        with pytest.raises(Exception):
            view_func2()
        assert len(User.query.all()) == 1
        assert len(session.query(User).all()) == 1

    def test_transaction_decorator_nested_2(self, session):
        @transaction(db)
        def create_user1():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)
            db.session.commit()

        @transaction(db)
        def create_user2(raise_exception=True):
            user = User(username='test2', email='2@b.com', password='1')
            db.session.add(user)
            db.session.commit()
            if raise_exception:
                raise Exception('')

        @transaction(db)
        def view_func(raise_exception=True):
            create_user1()
            assert User.query.first() is not None
            create_user2(raise_exception=raise_exception)

        # assert user1 and user2 all rollback
        with pytest.raises(Exception):
            view_func()
        assert len(User.query.all()) == 0
        assert len(session.query(User).all()) == 0

        # assert user1 and user2 all created
        view_func(raise_exception=False)
        assert len(User.query.all()) == 2
        assert len(session.query(User).all()) == 2

        def view_func2():
            create_user1()
            assert User.query.first() is not None
            create_user2()

        # assert user1 created and user2 rollback
        User.query.delete()
        db.session.commit()
        assert len(User.query.all()) == 0
        with pytest.raises(Exception):
            view_func2()
        assert len(User.query.all()) == 1
        assert len(session.query(User).all()) == 1
