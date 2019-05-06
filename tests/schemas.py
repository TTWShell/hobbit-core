from hobbit_core.schemas import ORMSchema, SchemaMixin

from marshmallow import fields

from .models import User


class UserSchema(ORMSchema, SchemaMixin):
    password = fields.Str(dump_only=True)

    class Meta:
        model = User
