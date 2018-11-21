import logging

from sqlalchemy.orm import exc as orm_exc

from .response import Result, ServerErrorResult, gen_response, RESP_MSGS

logger = logging.getLogger(__name__)


class ErrHandler(object):
    """Base error handler that catch all exceptions. Be sure response is::

        {
            "code": "404",  # error code, default is http status code, \
you can change it
            "message": "Not found",  # for alert in web page
            "detail": "id number field length must be 18",  # for debug
        }

    Examples::

        app.register_error_handler(Exception, ErrHandler.handler)
    """

    @classmethod
    def handler_werkzeug_exceptions(cls, e):
        return Result(gen_response(
            e.code, RESP_MSGS.get(e.code, e.name),
            None if not hasattr(e, 'data') else e.data['messages']),
            status=e.code)

    @classmethod
    def handler_sqlalchemy_orm_exc(cls, e):
        code, message, detail = 500, RESP_MSGS[500], repr(e)

        if isinstance(e, orm_exc.NoResultFound):
            code, message, detail = 404, u'源数据未找到', repr(e)

        return Result(gen_response(code, message, detail), status=code)

    @classmethod
    def handler_assertion_error(cls, e):
        code, message, detail = 422, str(e), repr(e)
        return Result(gen_response(code, message, detail), status=code)

    @classmethod
    def handler_others(cls, e):
        logging.error('UncheckedException:', exc_info=1)
        return ServerErrorResult(code=500, detail=repr(e))

    @classmethod
    def handler(cls, e):
        exc = 'others'
        if hasattr(e, '__module__'):
            exc = e.__module__.replace('.', '_')
        elif isinstance(e, AssertionError):
            exc = 'assertion_error'
        return getattr(cls, 'handler_{}'.format(exc), cls.handler_others)(e)
