# -*- encoding: utf-8 -*-
from marshmallow_enum import EnumField

from hobbit_core.schemas import ModelSchema

from .test_app.exts import db
from .test_app.models import User, RoleEnum

from . import BaseTest


class TestSchema(BaseTest):

    def test_model_schema(self, client):

        class UserSchema(ModelSchema):
            role = EnumField(RoleEnum)
            pass

            class Meta:
                model = User
                include_relationships = True
                load_instance = True

        assert UserSchema.Meta.dateformat == '%Y-%m-%d %H:%M:%S'

        user = User(username='name', email='admin@test', role=RoleEnum.admin)
        db.session.add(user)
        db.session.commit()

        data = UserSchema().dump(user)
        print(data)
        assert data['role'] == {'key': 1, 'label': 'admin', 'value': '管理员'}

        class UserSchema(ModelSchema):
            role = EnumField(RoleEnum)

            class Meta:
                model = User
                verbose = False

        data = UserSchema().dump(user)
        assert data['role'] == {'key': 1, 'value': '管理员'}

        payload = {'username': 'name', 'email': 'admin@test'}
        for role in (RoleEnum.admin.name,  RoleEnum.admin.value[0],
                     RoleEnum.admin.value[1]):
            payload['role'] = role
            assert UserSchema().load(payload) == {
                'role': RoleEnum.admin, 'email': 'admin@test',
                'username': 'name',
            }
        db.session.commit()
