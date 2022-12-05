import pytest

from webargs.core import ValidationError

from hobbit_core.pagination import PageParams, pagination

from . import BaseTest
from .test_app.models import User
from .test_app.exts import db


class TestPagination(BaseTest):

    def test_page_params(self, web_request, parser):
        # test default
        @parser.use_kwargs(PageParams, web_request, location='query')
        def viewfunc(page, page_size, order_by):
            return {'page': page, 'page_size': page_size, 'order_by': order_by}

        assert viewfunc() == {'order_by': ['-id'], 'page': 1, 'page_size': 10}

        # test page_size_range
        web_request.query = {'page_size': 101}
        msg = r".*page_size': .*Must be greater than or equal to 5 and" + \
            " less than or equal to 100.*"
        with pytest.raises(ValidationError, match=msg):
            print(viewfunc())

        # test order_by
        web_request.query = {'order_by': 'id,-11'}
        msg = r".*order_by': .*String does not match expected pattern.*"
        with pytest.raises(ValidationError, match=msg):
            viewfunc()

        web_request.query = {'order_by': 'id,-aaa'}
        assert viewfunc() == {
            'order_by': ['id', '-aaa'], 'page': 1, 'page_size': 10}

        web_request.query = {'order_by': ''}
        assert viewfunc() == {'order_by': [], 'page': 1, 'page_size': 10}

    def test_pagination(self, client):
        user1 = User(username='test1', email='1@b.com', password='1')
        user2 = User(username='test2', email='1@a.com', password='1')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        db.session.refresh(user1)
        db.session.refresh(user2)

        # test ?order_by= worked
        resp = pagination(User, 1, 10, order_by=[''])
        print(resp)
        assert resp['total'] == 2
        assert resp['page_size'] == 10
        assert resp['page'] == 1
        assert [i.id for i in resp['items']] == [user1.id, user2.id]

        # test order_by: str
        resp = pagination(User, 1, 10, order_by='role')
        assert [i.id for i in resp['items']] == [user1.id, user2.id]

        resp = pagination(User, 1, 10, order_by=['role', '-id'])
        assert [i.id for i in resp['items']] == [user2.id, user1.id]

        resp = pagination(User, 1, 10, order_by=['role', 'username'])
        assert [i.id for i in resp['items']] == [user1.id, user2.id]

        with pytest.raises(Exception, match='first arg obj must be model.'):
            pagination('User', 1, 10, order_by='role')

        msg = r'columns .*roles.* not exist in {} model'.format(User)
        with pytest.raises(Exception, match=msg):
            pagination(User, 1, 10, order_by='roles')
        db.session.commit()
