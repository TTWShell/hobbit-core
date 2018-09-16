from flask.json import dumps
from werkzeug import Response
from sqlalchemy.orm import exc as orm_exc


class Result(Response):

    def __init__(self, response=None, status=400, headers=None,
                 mimetype='application/json', content_type=None,
                 direct_passthrough=False):
        return super().__init__(
            response=dumps(response, indent=0, separators=(',', ':')) + '\n',
            status=status, headers=headers, mimetype=mimetype,
            content_type=content_type, direct_passthrough=direct_passthrough)


class ErrHandler:

    @classmethod
    def handler_werkzeug_exceptions(cls, e):
        return Result({
            'code': e.code, 'message': e.name,
            'detail': None if not hasattr(e, 'data') else e.data['messages'],
        }, status=e.code)

    @classmethod
    def handler_sqlalchemy_orm_exc(cls, e):
        code, message, detail = 500, '服务器内部错误', repr(e)

        if isinstance(e, orm_exc.NoResultFound):
            code, message, detail = 404, '源数据未找到', repr(e)

        return Result({
            'code': code, 'message': message, 'detail': detail}, status=code)

    @classmethod
    def handler_others(cls, e):
        return Result({
            'code': 500, 'message': '服务器内部错误', 'detail': repr(e),
        }, status=500)

    @classmethod
    def handler(cls, e):
        exc = 'others' if not hasattr(e, '__module__') else \
            e.__module__.replace('.', '_')
        return getattr(cls, 'handler_{}'.format(exc))(e)
