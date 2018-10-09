# -*- encoding: utf-8 -*-
from collections import Mapping
from flask_sqlalchemy import model

from marshmallow import fields
from webargs.fields import DelimitedList

from .utils import dict2object


class ParamsDict(dict):
    """Just available update func.

    Example::

        @use_kwargs(PageParams.update({...}))
        def list_users(page, page_size, order_by):
            pass

    """

    def update(self, other=None):
        """Update self by other Mapping and return self.
        """
        ret = self.copy()
        if other is not None:
            for k, v in other.items() if isinstance(other, Mapping) else other:
                ret[k] = v
        return ret


#: Base params for list view func.
PageParams = ParamsDict(
    page=fields.Int(missing=1, required=False),
    page_size=fields.Int(missing=10, required=False),
    order_by=DelimitedList(
        fields.String(missing='id'), required=False, missing=['id']),
)
"""Base params for list view func which contains ``page``、``page_size``、\
   ``order_by`` params.

    Example::

        @use_kwargs(PageParams)
        def list_users(page, page_size, order_by):
            pass
"""


def pagination(obj, page, page_size, order_by='id', query_exp=None):
    """A pagination for sqlalchemy query.

    Args:
        obj (db.Model): Model class like User.
        page (int): Page index.
        page_size (int): Row's count per page.
        order_by (str, list): Example: 'id'、['-id', 'column_name'].
        query_exp (flask_sqlalchemy.BaseQuery): Query like \
            ``User.query.filter_by(id=1)``.

    Returns:
        class: Class that contains ``items``、``page``、``page_size`` and \
            ``total`` fileds.
    """
    if not isinstance(obj, model.DefaultMeta):
        raise Exception('first arg obj must be model.')

    if not isinstance(order_by, list):
        order_by = [order_by]

    columns = {i.name for i in obj.__table__.columns}
    diff = {c.lstrip('-') for c in order_by} - columns
    if diff:
        raise Exception('columns {} not exist in {} model'.format(diff, obj))

    order_exp = []
    for column in order_by:
        if column.startswith('-'):
            order_exp.append(getattr(obj, column.lstrip('-')).desc())
        else:
            order_exp.append(getattr(obj, column))

    qexp = query_exp or getattr(obj, 'query')

    items = qexp.order_by(*order_exp).paginate(
        page, page_size, error_out=False)

    return dict2object({
        'items': items.items, 'page': page, 'page_size': page_size,
        'total': items.total,
    })
