import pytest

from webargs.core import Parser

from .test_app.run import app as tapp
from .test_app.exts import db as tdb


@pytest.fixture(scope='session')
def app(request):
    ctx = tapp.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return tapp


@pytest.fixture(scope='session')
def client(app, request):
    return app.test_client()


@pytest.fixture(scope='function')
def assert_session(app):
    with app.app_context():
        conn = tdb.engine.connect()
        options = dict(bind=conn, binds={})
        sess = tdb._make_scoped_session(options=options)
        assert sess.autocommit is False
        yield sess
        sess.remove()


@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        sess = tdb.session
        assert sess.autocommit is False
        return sess


@pytest.fixture(scope='function', params=['db_session'])
def session(request):
    return request.getfixturevalue(request.param)


#  borrowed from webargs
class MockRequestParser(Parser):
    """A minimal parser implementation that parses mock requests."""

    def load_querystring(self, req, schema):
        return req.query


@pytest.fixture
def request_context(app):
    """create the app and return the request context as a fixture
       so that this process does not need to be repeated in each test
    """
    return app.test_request_context


@pytest.yield_fixture(scope="function")
def web_request(request_context):
    with request_context():
        from flask import request
        req = request  # mock.Mock()
        req.query = {}
        yield req
        req.query = {}


@pytest.fixture
def parser():
    return MockRequestParser()
