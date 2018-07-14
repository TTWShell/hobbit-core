from flask import current_app
from marshmallow import fields

ma = current_app.hobbit_manager.ma


class PagedSchema(ma.Schema):
    total = fields.Int()
    page = fields.Int(missing=1, default=1)
    page_size = fields.Int(missing=10, default=10)

    class Meta:
        strict = True
