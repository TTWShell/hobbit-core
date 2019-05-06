from marshmallow import (
    Schema as Schema_, fields, pre_load, post_load, post_dump,
)
from marshmallow_sqlalchemy.schema import ModelSchemaMeta
from flask_marshmallow.sqla import ModelSchema as ModelSchema_
from marshmallow_enum import EnumField


class ORMSchema(ModelSchema_):
    """Base schema for ModelSchema. See `webargs/issues/126
    <https://github.com/sloria/webargs/issues/126>`_.

    Example::

        from hobbit_core.schemas import ORMSchema


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

        from hobbit_core.schemas import SchemaMixin

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


class PagedSchema(Schema_):
    """Base schema for list api pagination.

    Example::

        from marshmallow import fields

        from hobbit_core.schemas import PagedSchema

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
    """EnumSetMeta is a metaclass that can be used to auto generate load and
    dump func for EnumField.
    """

    @classmethod
    def gen_func(cls, decorator, field_name, enum, verbose=True):

        @decorator
        def wrapper(self, data):
            if data.get(field_name) is None:
                return data

            if decorator is pre_load:
                data[field_name] = enum.load(data[field_name])
            elif decorator is post_dump:
                data[field_name] = enum.dump(data[field_name], verbose)
            else:
                raise Exception(
                    'hobbit_core: decorator `{}` not support'.format(
                        decorator))

            return data
        return wrapper

    def __new__(cls, name, bases, attrs):
        schema = ModelSchemaMeta.__new__(cls, name, tuple(bases), attrs)
        verbose = getattr(schema.Meta, 'verbose', True)

        setattr(schema.Meta, 'dateformat', '%Y-%m-%d %H:%M:%S')

        for field_name, declared in schema._declared_fields.items():
            if not isinstance(declared, EnumField):
                continue

            setattr(schema, 'load_{}'.format(field_name), cls.gen_func(
                pre_load, field_name, declared.enum))
            setattr(schema, 'dump_{}'.format(field_name), cls.gen_func(
                post_dump, field_name, declared.enum, verbose=verbose))

        return schema


class ModelSchema(ORMSchema, SchemaMixin, metaclass=EnumSetMeta):
    """Base ModelSchema for ``class Model(db.SurrogatePK)``.

    * Auto generate load and dump func for EnumField.
    * Auto dump_only for ``id``, ``created_at``, ``updated_at`` fields.
    * Auto set dateformat to ``'%Y-%m-%d %H:%M:%S'``.
    * Auto use verbose for dump EnumField. See ``db.EnumExt``. You can define
      verbose in ``Meta``.

    Example::

        class UserSchema(ModelSchema):
            role = EnumField(RoleEnum)

            class Meta:
                model = User

        data = UserSchema().dump(user).data
        assert data['role'] == {'key': 1, 'label': 'admin', 'value': '管理员'}

    """
    pass
