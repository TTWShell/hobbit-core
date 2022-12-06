from typing import Optional, Any
from mypy_extensions import TypedDict

from flask.json import dumps
from flask import current_app, Response

RESP_MSGS = {
    200: 'ok',

    400: 'failed',
    401: '未登录',
    403: '未授权',
    404: '不正确的链接地址',
    422: '请求数据校验失败',

    500: '服务器内部错误',
}


class RespType(TypedDict):
    code: str
    message: str
    detail: Any


def gen_response(code: int, message: str = None, detail: Optional[str] = None,
                 data=None) -> RespType:
    """Func for generate response body.

    Args:
        code (string, int): Extension to interact with web pages. Default is \
            http response ``status_code`` like 200、404.
        message (string): For popup windows.
        data (object): Real response payload.
        detail (object): For debug, detail server error msg.

    Returns:
        dict: A dict contains all args.

    2021-07-08 Updated:
        Default type of `code` in response is force conversion to `str`, now
        support set `HOBBIT_USE_CODE_ORIGIN_TYPE = True` to return origin type.

    2021-07-13 Updated:
        Support set `HOBBIT_RESPONSE_MESSAGE_MAPS` to use self-defined
        response message. `HOBBIT_RESPONSE_MESSAGE_MAPS` must be dict.
    """
    use_origin_type = current_app.config.get(
        'HOBBIT_USE_CODE_ORIGIN_TYPE', False)

    resp_msgs = current_app.config.get('HOBBIT_RESPONSE_MESSAGE_MAPS', {})
    assert isinstance(resp_msgs, dict), \
        'HOBBIT_RESPONSE_MESSAGE_MAPS must be dict type.'
    if not message:
        message = resp_msgs.get(code)
        if message is None:
            message = RESP_MSGS.get(code, 'unknown')
    return {
        'code': str(code) if use_origin_type is False else code,
        'message': message,  # type: ignore
        'data': data,
        'detail': detail,
    }


class Result(Response):
    """Base json response.
    """
    _hobbit_status = 200  # type: ignore

    def __init__(self, response=None, status=None, headers=None,
                 mimetype='application/json', content_type=None,
                 direct_passthrough=False):
        assert sorted(response.keys()) == [
            'code', 'data', 'detail', 'message'], \
            'Error response, must include keys: code, data, detail, message'
        super().__init__(
            response=dumps(response, indent=0, separators=(',', ':')) + '\n',
            status=status if status is not None else self._hobbit_status,
            headers=headers, mimetype=mimetype,
            content_type=content_type, direct_passthrough=direct_passthrough)


class SuccessResult(Result):
    """Success response. Default status is 200, you can cover it by status arg.
    """
    _hobbit_status = 200

    def __init__(self, message: str = '', code: Optional[int] = None,
                 detail: Any = None, status: Optional[int] = None, data=None):
        super().__init__(
            gen_response(code if code is not None else self._hobbit_status,
                         message, detail, data),
            status or self._hobbit_status)


class FailedResult(Result):
    """Failed response. status always 400.
    """
    _hobbit_status = 400

    def __init__(self, message: str = '', code: Optional[int] = None,
                 detail: Any = None):
        super().__init__(
            gen_response(
                code if code is not None else self._hobbit_status,
                message, detail),
            self._hobbit_status)


class UnauthorizedResult(FailedResult):
    _hobbit_status = 401


class ForbiddenResult(FailedResult):
    _hobbit_status = 403


class ValidationErrorResult(FailedResult):
    _hobbit_status = 422


class ServerErrorResult(FailedResult):
    _hobbit_status = 500
