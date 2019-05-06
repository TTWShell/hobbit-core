# -*- encoding: utf-8 -*-
import pytest

from hobbit_core.response import gen_response, Result, \
    SuccessResult, FailedResult, UnauthorizedResult, ForbiddenResult, \
    ValidationErrorResult, ServerErrorResult

from . import BaseTest


class TestResponse(BaseTest):

    def test_gen_response(self):
        excepted = {'code': '1', 'message': u'未知错误', 'detail': None}
        assert excepted == gen_response(1)

        excepted = {'code': '1', 'message': u'测试', 'detail': ['1']}
        assert excepted == gen_response(1, u'测试', ['1'])

    def test_result(self):
        msg = 'Error response, must include keys: code, detail, message'
        with pytest.raises(AssertionError, match=msg):
            Result({})

        response = {'code': '1', 'message': u'未知错误', 'detail': None}
        result = Result(response)
        assert result.status_code == 200

        result = Result(response, status=201)
        assert result.status_code == 201

    def test_success_result(self):
        # assert status can rewrite
        excepted = b'{\n"code":"200",\n"detail":null,\n"message":"message"\n}\n'  # NOQA
        result = SuccessResult('message', status=301)
        assert result.status_code == 301
        assert excepted == result.data

        # assert default is 200
        result = SuccessResult()
        assert result.status_code == 200

    def test_failed_result(self):
        result = FailedResult()
        assert result.status_code == 400

    def test_results(self):
        excepted = {
            UnauthorizedResult: 401, ForbiddenResult: 403,
            ValidationErrorResult: 422, ServerErrorResult: 500,
        }
        for result, status_code in excepted.items():
            assert result().status_code == status_code
