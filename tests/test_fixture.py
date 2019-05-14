from .test_app.models import User
from .test_app.exts import db

from . import BaseTest


class TestFixture(BaseTest):

    def test_session(self, assert_session):
        """assert session is isolated from db.session
        """
        assert assert_session is not db.session

        user = User(username='test1', email='1@b.com', password='1')
        db.session.add(user)
        assert User.query.first() is not None
        assert assert_session.query(User).first() is None

        db.session.commit()
        assert User.query.first() is not None
        db.session.remove()
        assert User.query.first() is not None
        assert assert_session.query(User).first() is not None

        User.query.delete()
        assert User.query.first() is None
        assert assert_session.query(User).first() is not None

        db.session.commit()
        assert User.query.first() is None
        db.session.remove()
        assert User.query.first() is None
        assert assert_session.query(User).first() is None
