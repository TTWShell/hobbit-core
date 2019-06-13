# -*- encoding: utf-8 -*-
from hobbit_core.db import Column, BaseModel, EnumExt

from .exts import db


class RoleEnum(EnumExt):
    admin = (1, '管理员')
    normal = (2, '普通用户')


class User(BaseModel):
    username = Column(db.String(50), nullable=False, unique=True)
    email = Column(db.String(50), nullable=False, unique=True)
    password = Column(db.String(255), nullable=False, server_default='')
    role = Column(db.Enum(RoleEnum), doc='角色', default=RoleEnum.admin)


class Role(BaseModel):  # just for assert multi model worked
    name = Column(db.String(50), nullable=False, unique=True)
