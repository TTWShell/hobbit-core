from flask_sqlalchemy import SQLAlchemy

from hobbit_core.db import SurrogatePK, Column, BaseModel

db = SQLAlchemy()


class User(SurrogatePK, db.Model):  # type: ignore
    username = Column(db.String(20), unique=True, nullable=False,
                      doc='username')
    nick = Column(db.String(20), unique=True, nullable=False, doc='nick name')


class OtherUser(BaseModel):
    username = Column(db.String(20), unique=True, nullable=False,
                      doc='username')
    nick = Column(db.String(20), unique=True, nullable=False, doc='nick name')
