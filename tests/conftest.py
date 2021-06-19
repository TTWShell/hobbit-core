import pytest
from unittest import mock

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
        sess = tdb.create_scoped_session(options=options)
        assert sess.autocommit is False
        yield sess
        sess.remove()


@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        sess = tdb.session
        assert sess.autocommit is False
        return sess


@pytest.fixture(scope='function')
def auto_session(app):
    with app.app_context():
        conn = tdb.engine.connect()
        options = dict(bind=conn, binds={}, autocommit=True)
        sess = tdb.create_scoped_session(options=options)
        assert sess.autocommit is True
        yield sess
        sess.remove()


@pytest.fixture(scope='function', params=['db_session', 'auto_session'])
def session(request):
    return request.getfixturevalue(request.param)


#  borrowed from webargs
class MockRequestParser(Parser):
    """A minimal parser implementation that parses mock requests."""

    def parse_querystring(self, req, schema):
        return self.load_json(req, schema)

    def parse_json(self, req, schema):
        return self.load_json(req, schema)

    def parse_cookies(self, req, schema):
        return self.load_json(req, schema)


@pytest.yield_fixture(scope="function")
def web_request():
    req = mock.Mock()
    req.query = {}
    yield req
    req.query = {}


@pytest.fixture
def parser():
    return MockRequestParser()
