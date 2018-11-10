# -*- encoding: utf-8 -*-
import time
import pytest

from sqlalchemy.exc import ResourceClosedError
from hobbit_core.flask_hobbit.db import EnumExt, transaction

from . import BaseTest
from .exts import db
from .models import User


class TestSurrogatePK(BaseTest):

    def test_surrogate_pk(self, session):
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

        user = session.query(User).get(user_id)
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

    def clear_user(self):
        User.query.delete()
        db.session.commit()
        db.session.remove()
        assert User.query.all() == []

    def test_transaction_decorator(self, session):
        @transaction(db.session)
        def create_user(raise_exception):
            user1 = User(username='test1', email='1@b.com', password='1')
            db.session.add(user1)
            user2 = User(username='test2', email='2@b.com', password='1')
            db.session.add(user2)
            if raise_exception:
                raise Exception('')

        # assert user1 and user2 all rollback
        with pytest.raises(Exception, match=''):
            create_user(raise_exception=True)
        assert User.query.all() == []
        assert session.query(User).all() == []

        create_user(raise_exception=False)
        assert len(User.query.all()) == 2
        assert len(session.query(User).all()) == 2

        with pytest.raises(Exception, match=''):
            create_user(raise_exception=False)
            assert len(User.query.all()) == 2
            create_user(raise_exception=False)
        assert len(User.query.all()) == 2
        assert len(session.query(User).all()) == 2

    def test_can_not_used_with_commit_raised(self, app):
        @transaction(db.session)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)
            db.session.commit()

        msg = 'This transaction is closed'
        with pytest.raises(ResourceClosedError, match=msg):
            create_user()
        assert User.query.all() == []

    def test_used_with_begin_nested(self, session):
        @transaction(db.session)
        def create_user(commit_inner):
            with db.session.begin_nested():
                user = User(username='test1', email='1@b.com', password='1')
                db.session.add(user)

            with db.session.begin_nested():
                user = User(username='test2', email='2@b.com', password='1')
                db.session.add(user)
            if commit_inner:
                db.session.commit()

        create_user(commit_inner=False)
        assert len(session.query(User).all()) == 2

        self.clear_user()
        msg = 'This transaction is closed'
        with pytest.raises(ResourceClosedError, match=msg):
            create_user(commit_inner=True)
        assert len(session.query(User).all()) == 0

    def test_fall_used(self, session):
        @transaction(db.session)
        def create_user1():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)

        @transaction(db.session)
        def create_user2():
            user = User(username='test2', email='2@b.com', password='1')
            db.session.add(user)

        def view_func1():
            create_user1()
            create_user2()

        view_func1()
        assert len(session.query(User).all()) == 2

        # test exception
        self.clear_user()

        def view_func2():
            create_user1()
            raise Exception('')
            create_user2()

        with pytest.raises(Exception, match=''):
            view_func2()

        assert len(session.query(User).all()) == 1
        assert session.query(User).first().username == 'test1'

    def test_nested_self_raise(self, session):
        @transaction(db.session)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)

        @transaction(db.session)
        def view_func():
            create_user()

        msg = 'This transaction is closed'
        with pytest.raises(ResourceClosedError, match=msg):
            view_func()
        assert len(session.query(User).all()) == 0

    def test_nested_self_with_nested_arg_is_true(self, session):
        @transaction(db.session, nested=True)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)

        @transaction(db.session)
        def view_func():
            create_user()
            assert User.query.first() is not None

        create_user()
        assert len(session.query(User).all()) == 0
        self.clear_user()

        view_func()
        assert len(session.query(User).all()) == 1

    def test_nested_self_with_nested_arg_is_true_commit_raise(self, session):
        @transaction(db.session, nested=True)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)
            db.session.commit()

        msg = 'This transaction is closed'
        with pytest.raises(ResourceClosedError, match=msg):
            create_user()

    def test_autocommittrue_not_excepted(self, auto_session, session):
        msg = 'This transaction is closed'
        with pytest.raises(ResourceClosedError, match=msg):
            with auto_session.begin():  # start a transaction
                user = User(username='test1', email='1@b.com', password='1')
                auto_session.add(user)
                auto_session.commit()

        assert len(session.query(User).all()) == 1

    def test_assert_autocommit_is_false_raised(self, auto_session):
        msg = r'May not as excepted when autocommit=True.*'
        with pytest.raises(AssertionError, match=msg):
            @transaction(auto_session)
            def create_user():
                pass
