from marshmallow import fields
from flask_marshmallow import Marshmallow

from hobbit_core.schemas import PagedSchema

ma = Marshmallow()


class UserSchema(ma.SQLAlchemyAutoSchema):  # type: ignore

    class Meta:
        from .models import OtherUser
        model = OtherUser


class PagedUserSchema(PagedSchema):
    items = fields.Nested('UserSchema', many=True)


user_schemas = UserSchema()
paged_user_schemas = PagedUserSchema()
