from mypy_extensions import TypedDict
from typing import Union, List

from flask_sqlalchemy import model

from marshmallow import fields
from marshmallow import validate
from webargs.fields import DelimitedList

from .utils import ParamsDict


#: Base params for list view func.
PageParams = ParamsDict(
    page=fields.Int(missing=1, required=False,
                    validate=validate.Range(min=1, max=2**31)),
    page_size=fields.Int(
        missing=10, required=False, validate=validate.Range(min=5, max=100)),
    order_by=DelimitedList(
        fields.String(validate=validate.Regexp(r'^-?[a-zA-Z_]*$')),
        required=False, missing=['-id']),
)
"""Base params for list view func which contains ``page``、``page_size``、\
   ``order_by`` params.

    Example::

        @use_kwargs(PageParams)
        def list_users(page, page_size, order_by):
            pass
"""


class PaginationType(TypedDict):
    items: list
    page: int
    page_size: int
    total: int


def pagination(obj: 'model.DefaultMeta', page: int, page_size: int,
               order_by: Union[str, List[str], None] = 'id', query_exp=None) \
        -> PaginationType:
    """A pagination for sqlalchemy query.

    Args:
        obj (db.Model): Model class like User.
        page (int): Page index.
        page_size (int): Row's count per page.
        order_by (str, list, None): Example: 'id'、['-id', 'column_name'].
        query_exp (flask_sqlalchemy.BaseQuery): Query like \
            ``User.query.filter_by(id=1)``.

    Returns:
        dict: Dict contains ``items``、``page``、``page_size`` and \
            ``total`` fileds.
    """
    if not isinstance(obj, model.DefaultMeta):
        raise Exception('first arg obj must be model.')

    qexp = query_exp or getattr(obj, 'query')

    if order_by:
        if not isinstance(order_by, list):
            order_by = [order_by]

        order_by = [i for i in order_by if i]  # exclude ''

        columns = {i.name for i in obj.__table__.columns}
        diff = {c.lstrip('-') for c in order_by} - columns
        if diff:
            raise Exception(f'columns {diff} not exist in {obj} model')

        order_exp = []
        for column in order_by:
            if column.startswith('-'):
                order_exp.append(getattr(obj, column.lstrip('-')).desc())
            else:
                order_exp.append(getattr(obj, column))
        qexp = qexp.order_by(*order_exp)

    items = qexp.paginate(page, page_size, error_out=False)
    return {
        'items': items.items, 'page': page, 'page_size': page_size,
        'total': items.total,
    }
