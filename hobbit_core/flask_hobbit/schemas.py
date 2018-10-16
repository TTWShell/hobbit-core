# -*- encoding: utf-8 -*-
from marshmallow import Schema, fields


class SchemaMixin(object):
    """ add 'id','created_at','updated_at' fields to schema
    Example::
        from marshmallow import Schema

        from hobbit_core.flask_hobbit.schemas import SchemaMixin

        class TurbineTypeSchema(Schema, SchemaMixin):
            pass
    """
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime('%Y-%m-%d %H:%M:%S', dump_only=True)
    updated_at = fields.DateTime('%Y-%m-%d %H:%M:%S', dump_only=True)

    class Meta:
        dump_only = ('id', 'created_at', 'updated_at')
        strict = True
        ordered = False
        dateformat = '%Y-%m-%d %H:%M:%S'


class PagedSchema(Schema):
    """Base schema for list api pagination.

    Example::

        from marshmallow import fields

        from hobbit_core.flask_hobbit.schemas import PagedSchema

        from . import models
        from .exts import ma


        class UserSchema(ma.ModelSchema):

            class Meta:
                model = models.User


        class PagedUserSchema(PagedSchema):
            items = fields.Nested('UserSchema', many=True)


        paged_user_schemas = PagedUserSchema()
    """
    total = fields.Int()
    page = fields.Int(missing=1, default=1)
    page_size = fields.Int(missing=10, default=10)

    class Meta:
        strict = True
