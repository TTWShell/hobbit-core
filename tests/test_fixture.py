from .models import User
from .exts import db

from . import BaseTest


class TestFixture(BaseTest):

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
