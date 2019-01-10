from marshmallow import fields
from flask_marshmallow import Marshmallow

from hobbit_core.flask_hobbit.schemas import PagedSchema

ma = Marshmallow()


class UserSchema(ma.ModelSchema):  # type: ignore

    class Meta:
        from .models import User
        model = User


class PagedUserSchema(PagedSchema):
    items = fields.Nested('UserSchema', many=True)


user_schemas = UserSchema()
paged_user_schemas = PagedUserSchema()
