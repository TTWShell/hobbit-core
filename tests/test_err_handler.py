import json

from sqlalchemy.orm import exc as orm_exc
from werkzeug import exceptions as wkz_exc

from hobbit_core.err_handler import ErrHandler, HobbitException

from . import BaseTest


class TestErrHandler(BaseTest):

    def test_assertion_error(self, app):
        resp = ErrHandler.handler(AssertionError('message'))
        assert resp.status_code == 422
        data = json.loads(resp.get_data())
        assert data['message'] == 'message'

    def test_sqlalchemy_orm_exc(self, app):
        resp = ErrHandler.handler(orm_exc.NoResultFound())
        assert resp.status_code == 404, resp.get_json()
        data = json.loads(resp.get_data())
        assert data['message'] == u'源数据未找到'

        resp = ErrHandler.handler(orm_exc.UnmappedError())
        assert resp.status_code == 500
        data = json.loads(resp.get_data())
        assert data['message'] == u'服务器内部错误'

    def test_werkzeug_exceptions(self, app):
        resp = ErrHandler.handler(wkz_exc.Unauthorized())
        assert resp.status_code == 401
        data = json.loads(resp.get_data())
        assert data['message'] == u'未登录'

    def test_hobbit_exception(self, app):
        resp = ErrHandler.handler(HobbitException('msg'))
        assert resp.status_code == 400
        data = json.loads(resp.get_data())
        assert data['message'] == 'msg'
        # py27,py36 == "Exception('msg',)"
        # py37 == "Exception('msg')"
        assert data['detail'].startswith("HobbitException('msg'")

    def test_others(self, app):
        resp = ErrHandler.handler(Exception('msg'))
        assert resp.status_code == 500
        data = json.loads(resp.get_data())
        assert data['message'] == u'服务器内部错误'
        # py27,py36 == "Exception('msg',)"
        # py37 == "Exception('msg')"
        assert data['detail'].startswith("Exception('msg'")
