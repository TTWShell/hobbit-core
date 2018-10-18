from hobbit_core.flask_hobbit.db import Column, SurrogatePK

from .exts import db


class User(SurrogatePK, db.Model):
    username = Column(db.String(50), nullable=True, unique=True)
    email = Column(db.String(50), nullable=True, unique=True)
    password = Column(db.String(255), nullable=False, server_default='')
