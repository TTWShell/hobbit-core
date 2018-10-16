# -*- encoding: utf-8 -*-
from marshmallow import Schema, fields, post_load
from flask_marshmallow.sqla import ModelSchema


class ORMSchema(ModelSchema):
    """Base schema for ModelSchema. See `webargs/issues/126
    <https://github.com/sloria/webargs/issues/126>`_.

    Example::

        from hobbit_core.flask_hobbit.schemas import ORMSchema


        class UserSchema(ORMSchema):

            class Meta:
                model = User
                load_only = ('password')

    ``@use_kwargs(UserSchema())`` use in combination with ``load_only``::

        @bp.route('/users/', methods=['POST'])
        @use_kwargs(UserSchema())
        def create_user(username, password):
            pass
    """

    @post_load()
    def make_instance(self, data):
        return data


class SchemaMixin(object):
    """Add ``id``, ``created_at``, ``updated_at`` fields to schema,
    default ``dump_only=True``.

    Example::

        from marshmallow import Schema

        from hobbit_core.flask_hobbit.schemas import SchemaMixin

        class UserSchema(Schema, SchemaMixin):
            pass
    """

    id = fields.Int(dump_only=True)
    created_at = fields.DateTime('%Y-%m-%d %H:%M:%S', dump_only=True)
    updated_at = fields.DateTime('%Y-%m-%d %H:%M:%S', dump_only=True)

    class Meta:
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
