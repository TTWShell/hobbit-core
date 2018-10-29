# -*- encoding: utf-8 -*-
from marshmallow_enum import EnumField

from hobbit_core.flask_hobbit.schemas import ModelSchema

from .exts import db
from . import BaseTest
from .models import User, RoleEnum


class TestSchema(BaseTest):

    def test_model_schema(self, client):

        class UserSchema(ModelSchema):
            role = EnumField(RoleEnum)

            class Meta:
                model = User

        user = User(username='name', email='admin@test', role=RoleEnum.admin)
        db.session.add(user)
        db.session.commit()

        data = UserSchema().dump(user).data
        assert data['role'] == {'key': 1, 'label': 'admin', 'value': '管理员'}
