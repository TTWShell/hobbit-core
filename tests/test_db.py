import time
import pytest
import random

from hobbit_core.db import EnumExt, transaction
from hobbit_core.db import BaseModel, Column

from .test_app.exts import db
from .test_app.models import User

from . import BaseTest


class TestSurrogatePK(BaseTest):

    def test_surrogate_pk(self, assert_session):
        user = User(username='test1', email='1@b.com', password='1')
        assert str(user).startswith('<User(')
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

        user = assert_session.query(User).get(user_id)
        assert user.created_at < user.updated_at


class TestBaseModel(BaseTest):

    @pytest.fixture(scope='class', params=[True, False])
    def upper_conf(self, app, request):
        app.config['HOBBIT_UPPER_SEQUENCE_NAME'] = request.param
        return request.param

    @pytest.mark.parametrize('conf, excepted', [
        [(None, None, []), ['username', 'id', 'created_at', 'updated_at']],
        [(None, 'user_id', []), [
            'username', 'user_id', 'created_at', 'updated_at']],
        [('changed', None, ['created_at', 'updated_at']), ['username', 'id']],
    ])
    def test_oracle(self, app, conf, excepted, upper_conf):

        class TestUser(BaseModel):
            __bind_key__ = 'oracle'
            __tablename__ = f'{random.random()}'

            sequence_name, primary_key_name, exclude_columns = conf

            username = Column(db.String(32), nullable=False, index=True)

        assert sorted([
            i.name for i in TestUser.__table__.columns]) == sorted(excepted)
        real_sequence_name = TestUser.__table__.columns[
            TestUser.primary_key_name or 'id'].default.name

        excepted_name = TestUser.sequence_name if TestUser.sequence_name else \
            'TestUser_{}_seq'.format(TestUser.primary_key_name or 'id')
        if upper_conf:
            assert real_sequence_name == excepted_name.upper()
        else:
            assert real_sequence_name == excepted_name


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

    def test_transaction_decorator(self, session, assert_session):
        @transaction(session)
        def create_user(raise_exception):
            user1 = User(username='test1', email='1@b.com', password='1')
            session.add(user1)
            user2 = User(username='test2', email='2@b.com', password='1')
            session.add(user2)
            if raise_exception:
                raise Exception('')

        # assert user1 and user2 all rollback
        with pytest.raises(Exception, match=''):
            create_user(raise_exception=True)
        assert assert_session.query(User).all() == []

        # assert user1 and user2 all created
        create_user(raise_exception=False)
        assert len(assert_session.query(User).all()) == 2

        self.clear_user()
        with pytest.raises(Exception, match=''):
            create_user(raise_exception=False)
            assert len(assert_session.query(User).all()) == 2
            create_user(raise_exception=False)

        assert len(assert_session.query(User).all()) == 2

    def test_used_with_commit_without_raised(self, session, assert_session):
        # > 1.4
        @transaction(session)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            session.add(user)
            session.commit()

        create_user()
        assert assert_session.query(User).all() != []

    def test_used_with_begin_nested(self, session, assert_session):
        # > 1.4
        @transaction(session)
        def create_user(commit_inner):
            with session.begin_nested():
                user = User(username='test1', email='1@b.com', password='1')
                session.add(user)

            with session.begin_nested():
                user = User(username='test2', email='2@b.com', password='1')
                session.add(user)
            if commit_inner:
                session.commit()

        create_user(commit_inner=False)
        assert len(assert_session.query(User).all()) == 2

        self.clear_user()
        create_user(commit_inner=True)
        assert len(assert_session.query(User).all()) == 2

    def test_fall_used(self, session, assert_session):
        @transaction(session)
        def create_user1():
            user = User(username='test1', email='1@b.com', password='1')
            session.add(user)

        @transaction(session)
        def create_user2():
            user = User(username='test2', email='2@b.com', password='1')
            session.add(user)

        def view_func1():
            create_user1()
            create_user2()

        view_func1()
        assert len(assert_session.query(User).all()) == 2

        # test exception
        self.clear_user()

        def view_func2():
            create_user1()
            raise Exception('')

        with pytest.raises(Exception, match=''):
            view_func2()

        assert len(assert_session.query(User).all()) == 1
        assert assert_session.query(User).first().username == 'test1'

    def test_nested_self_not_raise(self, session, assert_session):
        # > 1.4
        @transaction(session)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            db.session.add(user)

        @transaction(session)
        def view_func():
            user = User(username='test2', email='2@b.com', password='1')
            db.session.add(user)
            create_user()

        view_func()
        assert len(assert_session.query(User).all()) == 2

    def test_nested_self_with_nested_arg_is_true(
            self, session, assert_session):
        @transaction(session, nested=True)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            session.add(user)

        @transaction(session)
        def view_func():
            create_user()
            assert session.query(User).first() is not None

        view_func()
        assert len(assert_session.query(User).all()) == 1

    def test_nested_self_with_nested_arg_is_true_commit_not_raise(
            self, session, assert_session):
        @transaction(session, nested=True)
        def create_user():
            user = User(username='test1', email='1@b.com', password='1')
            session.add(user)
            session.commit()

        @transaction(session)
        def view_func():
            create_user()

        view_func()


class TestNestedSessionSignal(BaseTest):

    def test_transaction_signal_success(self, client, assert_session):
        email = "test@test.com"
        resp = client.post('/create_user/success/', json={"email": email})
        assert resp.status_code == 200

        user = assert_session.query(User).filter(User.email == email).first()
        assert user and user.username == "signalling_ok"

    def test_transaction_signal_dailed(self, client, assert_session):
        email = "test@test.com"
        resp = client.post('/create_user/failed/', json={"email": email})
        assert resp.status_code == 200

        user = assert_session.query(User).filter(User.email == email).first()
        assert user and user.username != "signalling_ok"
