from typing import Optional, Any
from mypy_extensions import TypedDict

from flask.json import dumps
from werkzeug import Response

RESP_MSGS = {
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


def gen_response(code: int, message: str = '', detail: Optional[str] = None) \
        -> RespType:
    """Func for generate response body.

    Args:
        code (string, int): Extension to interact with web pages. Default is \
            http response ``status_code`` like 200、404.
        message (string): For popup windows.
        detail (object): For debug, detail server error msg.

    Returns:
        dict: A dict contains all args.

    """
    return {
        'code': str(code),
        'message': message or RESP_MSGS.get(code, '未知错误'),  # type: ignore
        'detail': detail,
    }


class Result(Response):
    """Base json response.
    """
    status = 200  # type: ignore

    def __init__(self, response=None, status=None, headers=None,
                 mimetype='application/json', content_type=None,
                 direct_passthrough=False):
        assert sorted(response.keys()) == ['code', 'detail', 'message'], \
            'Error response, must include keys: code, detail, message'
        super(Result, self).__init__(
            response=dumps(response, indent=0, separators=(',', ':')) + '\n',
            status=status or self.status, headers=headers, mimetype=mimetype,
            content_type=content_type, direct_passthrough=direct_passthrough)


class SuccessResult(Result):
    """Success response. Default status is 200, you can cover it by status arg.
    """
    status = 200

    def __init__(self, message: str = '', code: Optional[int] = None,
                 detail: Any = None, status: Optional[int] = None):
        super(SuccessResult, self).__init__(
            gen_response(code or self.status, message, detail),
            status or self.status)


class FailedResult(Result):
    """Failed response. status always 400.
    """
    status = 400

    def __init__(self, message: str = '', code: Optional[int] = None,
                 detail: Any = None):
        super(FailedResult, self).__init__(
            gen_response(code or self.status, message, detail), self.status)


class UnauthorizedResult(FailedResult):
    status = 401


class ForbiddenResult(FailedResult):
    status = 403


class ValidationErrorResult(FailedResult):
    status = 422


class ServerErrorResult(FailedResult):
    status = 500
