import pytest
try:
    from unittest import mock
except ImportError:
    import mock  # python2

from webargs.core import Parser, get_value

from .run import app as tapp


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


#  borrowed from webargs
class MockRequestParser(Parser):
    """A minimal parser implementation that parses mock requests."""

    def parse_querystring(self, req, name, field):
        return get_value(req.query, name, field)

    def parse_json(self, req, name, field):
        return get_value(req.json, name, field)

    def parse_cookies(self, req, name, field):
        return get_value(req.cookies, name, field)


@pytest.yield_fixture(scope="function")
def web_request():
    req = mock.Mock()
    req.query = {}
    yield req
    req.query = {}


@pytest.fixture
def parser():
    return MockRequestParser()
