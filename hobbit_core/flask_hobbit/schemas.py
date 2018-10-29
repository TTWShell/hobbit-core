# -*- encoding: utf-8 -*-
import six

from marshmallow import Schema, fields, pre_load, post_load, post_dump
from marshmallow_sqlalchemy.schema import ModelSchemaMeta
from flask_marshmallow.sqla import ModelSchema
from marshmallow_enum import EnumField


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


class EnumSetMeta(ModelSchemaMeta):
    """Auto generate load and dump func for EnumField.
    """

    @classmethod
    def gen_func(cls, decorator, field_name, enum):

        @decorator
        def wrapper(self, data):
            if data.get(field_name) is None:
                return data

            if decorator is pre_load:
                data[field_name] = enum.load(data['label'])
            if decorator is post_dump:
                data[field_name] = enum.dump(data['label'])
            else:
                raise Exception(
                    'hobbit_core: decorator `{}` not support'.format(
                        decorator))

            return data
        return wrapper

    def __new__(cls, name, bases, attrs):
        schema = ModelSchemaMeta.__new__(cls, name, tuple(bases), attrs)

        for field_name, declared in schema._declared_fields.items():
            if not isinstance(declared, EnumField):
                continue

            setattr(schema, 'load_{}'.format(field_name),
                    cls.gen_func(pre_load, field_name, declared.enum))
            setattr(schema, 'dump_{}'.format(field_name),
                    cls.gen_func(post_dump, field_name, declared.enum))

        return schema


@six.add_metaclass(EnumSetMeta)
class ModelSchema(ORMSchema, SchemaMixin):
    pass
