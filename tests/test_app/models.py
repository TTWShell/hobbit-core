# -*- encoding: utf-8 -*-
from sqlalchemy import UniqueConstraint, func, DateTime, BigInteger
from flask_sqlalchemy import models_committed

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


@models_committed.connect
def signalling(app, changes, **kwargs):
    for instance, operation in changes:
        if instance.__tablename__ in [i.__tablename__ for i in [User]]:
            models_committed.disconnect(signalling)
            conn = db.engine.connect()
            options = dict(bind=conn, binds={})
            session = db._make_scoped_session(options=options)
            user = session.query(User).first()
            if user and user.username == 'signalling_test':
                user.username = 'signalling_ok'
                session.merge(user)
                session.commit()
            session.remove()
            models_committed.connect(signalling)
            break


class Role(BaseModel):  # just for assert multi model worked
    name = Column(db.String(50), nullable=False, unique=True)


class BulkModelMixin:
    x = Column(db.String(50), nullable=False)
    y = Column(db.String(50), nullable=False)
    z = Column(db.String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint('x', 'y', 'z', name='bulk_model_main_unique_key'),
    )


class BulkModel2Mixin:
    id = Column(BigInteger, primary_key=True)
    update = Column(
        DateTime, index=True, nullable=False, server_default=func.now(),
        onupdate=func.now())
    x = Column(db.String(50), nullable=False)
    y = Column(db.String(50), nullable=False)
    z = Column(db.String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint('x', 'y', 'z', name='bulk_model2_main_unique_key'),
    )


class BulkModel(BaseModel, BulkModelMixin):
    pass


class BulkModel2(db.Model, BulkModel2Mixin):
    pass


class BulkModelMysql(BaseModel, BulkModelMixin):
    __bind_key__ = 'mysql'


class BulkModel2Mysql(db.Model, BulkModel2Mixin):
    __bind_key__ = 'mysql'
