import pytest
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
