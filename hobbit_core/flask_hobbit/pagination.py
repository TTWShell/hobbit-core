from collections import Mapping
from flask_sqlalchemy import model

from marshmallow import fields
from webargs.fields import DelimitedList


class ParamsDict(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self, other=None):
        ret = self.copy()
        if other is not None:
            for k, v in other.items() if isinstance(other, Mapping) else other:
                ret[k] = v
        return ret


PageParams = ParamsDict(
    page=fields.Int(missing=1, required=False),
    page_size=fields.Int(missing=10, required=False),
    order_by=DelimitedList(
        fields.String(missing='id'), required=False, missing=['id']),
)


def pagination(obj, page, page_size, order_by='id', query_exp=None):
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

    class Result:
        pass

    Result.items = items.items
    Result.page = page
    Result.opage_size = page_size
    Result.total = items.total

    return Result
