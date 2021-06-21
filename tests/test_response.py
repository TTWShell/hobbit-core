# -*- encoding: utf-8 -*-
import pytest

from hobbit_core.response import gen_response, Result, \
    SuccessResult, FailedResult, UnauthorizedResult, ForbiddenResult, \
    ValidationErrorResult, ServerErrorResult

from . import BaseTest


class TestResponse(BaseTest):

    @pytest.mark.parametrize('input_, excepted', [
        ((1, ), {
            'code': '1', 'message': '未知错误', 'detail': None, 'data': None}),
        ((1, '测试', ['1'], {}), {
            'code': '1', 'message': '测试', 'detail': ['1'], 'data': {}}),
        ((1, '测试', ['1'], []), {
            'code': '1', 'message': '测试', 'detail': ['1'], 'data': []}),
    ])
    def test_gen_response(self, input_, excepted):
        assert excepted == gen_response(*input_)

    def test_result(self):
        msg = 'Error response, must include keys: code, data, detail, message'
        with pytest.raises(AssertionError, match=msg):
            Result({})

        response = {
            'code': '1', 'message': u'未知错误', 'detail': None, 'data': None}
        result = Result(response)
        assert result.status_code == 200

        result = Result(response, status=201)
        assert result.status_code == 201

    def test_success_result(self):
        # assert status can rewrite
        excepted = b'{\n"code":"200",\n"data":null,\n"detail":null,\n"message":"message"\n}\n'  # NOQA
        result = SuccessResult('message', status=301)
        assert result.status_code == 301
        assert excepted == result.data

        # assert default is 200
        result = SuccessResult()
        assert result.status_code == 200

    def test_failed_result(self):
        result = FailedResult()
        assert result.status_code == 400

    @pytest.mark.parametrize('result, excepted_status_code', [
        (UnauthorizedResult, 401),
        (ForbiddenResult, 403),
        (ValidationErrorResult, 422),
        (ServerErrorResult, 500),
    ])
    def test_results(self, result, excepted_status_code):
        assert result().status_code == excepted_status_code
