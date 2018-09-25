from marshmallow import Schema, fields


class PagedSchema(Schema):
    total = fields.Int()
    page = fields.Int(missing=1, default=1)
    page_size = fields.Int(missing=10, default=10)

    class Meta:
        strict = True
