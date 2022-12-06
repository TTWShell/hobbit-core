# -*- encoding: utf-8 -*-
import pytest

from hobbit_core.response import gen_response, Result, \
    SuccessResult, FailedResult, UnauthorizedResult, ForbiddenResult, \
    ValidationErrorResult, ServerErrorResult

from . import BaseTest


class TestResponse(BaseTest):

    @pytest.mark.parametrize('input_, excepted', [
        ((1, ), {
            'code': '1', 'message': 'unknown', 'detail': None, 'data': None}),
        ((1, '测试', ['1'], {}), {
            'code': '1', 'message': '测试', 'detail': ['1'], 'data': {}}),
        ((1, '测试', ['1'], []), {
            'code': '1', 'message': '测试', 'detail': ['1'], 'data': []}),
    ])
    def test_gen_response(self, app, input_, excepted):
        assert excepted == gen_response(*input_)

    def test_result(self):
        msg = 'Error response, must include keys: code, data, detail, message'
        with pytest.raises(AssertionError, match=msg):
            Result({})

        response = {
            'code': '1', 'message': u'unknown', 'detail': None, 'data': None}
        result = Result(response)
        print(result.__dict__)
        assert result.status_code == 200

        result = Result(response, status=201)
        assert result.status_code == 201

    def test_success_result(self, app):
        # assert status can rewrite
        excepted = b'{\n"code":"200",\n"data":null,\n"detail":null,\n"message":"message"\n}\n'  # NOQA
        result = SuccessResult('message', status=301)
        assert result.status_code == 301
        assert excepted == result.data

        # assert default is 200
        result = SuccessResult()
        assert result.status_code == 200

        app.config['HOBBIT_USE_CODE_ORIGIN_TYPE'] = True
        result = SuccessResult(code=0)
        assert b'"code":0' in result.data

        app.config['HOBBIT_USE_CODE_ORIGIN_TYPE'] = False
        result = SuccessResult(code=0)
        assert b'"code":"0"' in result.data

        app.config['HOBBIT_RESPONSE_MESSAGE_MAPS'] = {100: 'testmsg'}
        result = SuccessResult(code=100)
        assert b'"message":"testmsg"' in result.data
        app.config['HOBBIT_RESPONSE_MESSAGE_MAPS'] = {}

    def test_failed_result(self):
        result = FailedResult()
        assert result.status_code == 400

    @pytest.mark.parametrize('result, excepted_status', [
        (UnauthorizedResult, 401),
        (ForbiddenResult, 403),
        (ValidationErrorResult, 422),
        (ServerErrorResult, 500),
    ])
    def test_results(self, result, excepted_status):
        assert result().status_code == excepted_status
