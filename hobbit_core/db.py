from enum import Enum, EnumMeta
from functools import wraps
import warnings

from mypy_extensions import TypedDict
from typing import Any, Union, List, Dict

from flask import current_app
from sqlalchemy import BigInteger, Column, ForeignKey, func, DateTime, Sequence
from sqlalchemy.orm.session import Session
from flask_sqlalchemy import DefaultMeta

db = current_app.hobbit_manager.db


class _BaseModel:

    def __repr__(self) -> str:
        """You can set label property.

        Returns:
            str: ``<{classname}({pk}:{label!r})>``
        """
        class_name = self.__class__.__name__
        pk = self.id  # type: ignore
        label = getattr(self, "label", "")
        return f'<{class_name}({pk}:{label!r})>'


class SurrogatePK(_BaseModel):
    """A mixin that add ``id``、``created_at`` and ``updated_at`` columns
    to any declarative-mapped class.

    **id**: A surrogate biginteger 'primary key' column.

    **created_at**: Auto save ``datetime.now()`` when row created.

    **updated_at**: Auto save ``datetime.now()`` when row updated.

    **It is not recommended. See hobbit_core.db.BaseModel.**
    """

    __table_args__ = {'extend_existing': True}  # type: ignore

    id = Column(BigInteger, primary_key=True)
    created_at = Column(
        DateTime, index=True, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, index=True, nullable=False, server_default=func.now(),
        onupdate=func.now())

    def __init_subclass__(cls, **kwargs):
        msg = 'SurrogatePK is Deprecated. See hobbit_core.db.BaseModel.'
        warnings.warn(msg)
        super().__init_subclass__(**kwargs)


class BaseModelMeta(DefaultMeta):

    def __new__(cls, name, bases, attrs):
        if name in ('BaseModelMeta', 'BaseModel'):
            return super().__new__(cls, name, bases, attrs)

        primary_key_name = attrs.get('primary_key_name') or 'id'

        attrs[primary_key_name] = Column(BigInteger, primary_key=True)
        attrs['created_at'] = Column(
            DateTime, index=True, nullable=False, server_default=func.now())
        attrs['updated_at'] = Column(
            DateTime, index=True, nullable=False, server_default=func.now(),
            onupdate=func.now())

        if db.get_engine(bind_key=attrs.get('__bind_key__')).name == 'oracle':
            sequence_name = attrs.get('sequence_name') or \
                f'{name}_{primary_key_name}_seq'
            if current_app.config['HOBBIT_UPPER_SEQUENCE_NAME']:
                sequence_name = sequence_name.upper()
            attrs[primary_key_name] = Column(
                BigInteger,
                Sequence(sequence_name),
                primary_key=True)

        exclude_columns = attrs.get('exclude_columns', [])
        for column in exclude_columns:
            attrs.pop(column)

        return super().__new__(cls, name, bases, attrs)


class BaseModel(_BaseModel, db.Model, metaclass=BaseModelMeta):  # type: ignore # noqa
    """Abstract base model class contains
    ``id``、``created_at`` and ``updated_at`` columns.

    **id**: A surrogate biginteger 'primary key' column.

    **created_at**: Auto save ``datetime.now()`` when row created.

    **updated_at**: Auto save ``datetime.now()`` when row updated.

    Support **oracle id sequence**, default name is ``{class_name}_id_seq``,
    can changed by ``sequence_name`` and ``HOBBIT_UPPER_SEQUENCE_NAME`` config.
    Default value of app.config['HOBBIT_UPPER_SEQUENCE_NAME'] is False.

    Examples::

        from hobbit_core.db import Column, BaseModel

        class User(BaseModel):
            username = Column(db.String(32), nullable=False, index=True)

        print([i.name for i in User.__table__.columns])
        # ['username', 'id', 'created_at', 'updated_at']

    Can be blocked columns with **exclude_columns**::

        class User(BaseModel):
            exclude_columns = ['created_at', 'updated_at']
            username = Column(db.String(32), nullable=False, index=True)

        print([i.name for i in User.__table__.columns])
        # ['username', 'id']

    Can be changed primary_key's name using **primary_key_name**::

        class User(BaseModel):
            primary_key_name = 'user_id'
            username = Column(db.String(32), nullable=False, index=True)

        print([i.name for i in User.__table__.columns])
        # ['username', 'user_id', 'created_at', 'updated_at']

    Can be changed sequence's name using **sequence_name**
    (worked with oracle)::

        class User(BaseModel):
            sequence_name = 'changed'
            username = Column(db.String(32), nullable=False, index=True)

        # print(User.__table__.columns['id'])
        Column('id', ..., default=Sequence('changed_id_seq'))
    """

    __abstract__ = True


def reference_col(tablename: str, nullable: bool = False, pk_name: str = 'id',
                  onupdate: str = None, ondelete: str = None, **kwargs: Any) \
        -> Column:
    """Column that adds primary key foreign key reference.

    Args:
        tablename (str): Model.__table_name__.
        nullable (bool): Default is False.
        pk_name (str): Primary column's name.
        onupdate (str): If Set, emit ON UPDATE <value> when
          issuing DDL for this constraint. Typical values include CASCADE,
          DELETE and RESTRICT.
        ondelete (str): If set, emit ON DELETE <value> when
          issuing DDL for this constraint. Typical values include CASCADE,
          DELETE and RESTRICT.

    Others:

    See ``sqlalchemy.Column``.

    Examples::

        from sqlalchemy.orm import relationship

        role_id = reference_col('role')
        role = relationship('Role', backref='users', cascade='all, delete')
    """

    return Column(
        ForeignKey('{0}.{1}'.format(tablename, pk_name),
                   onupdate=onupdate, ondelete=ondelete),
        nullable=nullable, **kwargs)


class EnumExtMeta(EnumMeta):

    def __new__(cls, name, bases, attrs):
        obj = super(EnumExtMeta, cls).__new__(cls, name, bases, attrs)

        keys, values = set(), set()
        for _, member in obj.__members__.items():
            member = member.value
            if not isinstance(member, tuple) or len(member) != 2:
                raise TypeError(
                    u'EnumExt member must be tuple type and length equal 2.')
            key, value = member
            if key in keys or value in values:
                raise ValueError(u'duplicate values found: `{}`, please check '
                                 u'key or value.'.format(member))
            keys.add(key)
            values.add(key)

        return obj


class OptType(TypedDict, total=False):
    key: int
    value: str
    label: str


class EnumExt(Enum, metaclass=EnumExtMeta):
    """ Extension for serialize/deserialize sqlalchemy enum field.

    Be sure ``type(key)`` is ``int`` and ``type(value)`` is ``str``
    (``label = (key, value)``).

    Examples::

        class TaskState(EnumExt):
            # label = (key, value)
            CREATED = (0, '新建')
            PENDING = (1, '等待')
            STARTING = (2, '开始')
            RUNNING = (3, '运行中')
            FINISHED = (4, '已完成')
            FAILED = (5, '失败')
    """

    @classmethod
    def strict_dump(cls, label: str, verbose: bool = False) -> Union[int, str]:
        """Get key or value by label.

        Examples::

            TaskState.strict_dump('CREATED')  # 0
            TaskState.strict_dump('CREATED', verbose=True)  # '新建'

        Returns:
            int|str: Key or value, If label not exist, raise ``KeyError``.
        """

        return cls[label].value[1 if verbose else 0]

    @classmethod
    def dump(cls, label: str, verbose: bool = False) -> Dict[str, Any]:
        """Dump one label to option.

        Examples::

            TaskState.dump('CREATED')  # {'key': 0, 'value': '新建'}

        Returns:

            dict: Dict of label's key and value. If label not exist,
            raise ``KeyError``.
        """

        ret = {'key': cls[label].value[0], 'value': cls[label].value[1]}
        if verbose:
            ret.update({'label': label})
        return ret

    @classmethod
    def load(cls, val: Union[int, str]) -> str:  # type: ignore
        """Get label by key or value. Return val when val is label.

        Examples::

            TaskState.load('FINISHED')  # 'FINISHED'
            TaskState.load(4)  # 'FINISHED'
            TaskState.load('新建')  # 'CREATED'

        Returns:
            str|None: Label.
        """

        if val in cls.__members__:
            return val  # type: ignore

        pos = 1 if isinstance(val, str) else 0
        for elem in cls:
            if elem.value[pos] == val:
                return elem.name

    @classmethod
    def to_opts(cls, verbose: bool = False) -> List[Dict[str, Any]]:
        """Enum to options.

        Examples::

            opts = TaskState.to_opts(verbose=True)
            print(opts)

            [{'key': 0, 'label': 'CREATED', 'value': u'新建'}, ...]

        Returns:
            list: List of dict which key is `key`, `value`, label.
        """

        opts = []
        for elem in cls:
            opt = {'key': elem.value[0], 'value': elem.value[1]}
            if verbose:
                opt.update({'label': elem.name})
            opts.append(opt)
        return opts


def transaction(session: Session, nested: bool = False):
    """SQLAlchemy 1.4 deprecates “autocommit mode.
    See more: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html

    2022-05-18 Updated: Use `nested=None` to prevent signal bug, See more:
    https://github.com/pallets-eco/flask-sqlalchemy/issues/645

    Tips:
        * **Can't** do ``session.commit()`` **in func**,
        **otherwise unknown beloved**.

        * **Must use the same session in decorator and decorated function**.

        * **We can use nested** if keep top decorated
          by ``@transaction(session, nested=False)`` and all subs decorated
          by ``@transaction(session, nested=True)``.

    Examples::

        from hobbit_core.db import transaction

        from app.exts import db


        @bp.route('/users/', methods=['POST'])
        @transaction(db.session)
        def create(username, password):
            user = User(username=username, password=password)
            db.session.add(user)
            # db.session.commit() error

    We can nested use this decorator. Must set ``nested=True`` otherwise
    raise ``ResourceClosedError`` (session.autocommit=False) or
    raise ``InvalidRequestError`` (session.autocommit=True)::

        @transaction(db.session, nested=True)
        def set_role(user, role):
            user.role = role
            # db.session.commit() error


        @bp.route('/users/', methods=['POST'])
        @transaction(db.session)
        def create(username, password):
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.flush()
            set_role(user, 'admin')
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if getattr(session, 'autocommit') is True and nested is False:
                session.begin()  # start a transaction
            try:
                if nested is None:
                    resp = func(*args, **kwargs)
                else:
                    with session.begin_nested():
                        resp = func(*args, **kwargs)
                if not nested:
                    # commit - begin(), transaction finished
                    session.commit()
            except Exception as e:
                if not nested:
                    session.rollback()
                    session.remove()
                raise e
            return resp
        return inner
    return wrapper
