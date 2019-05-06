from enum import Enum, EnumMeta
from functools import wraps
from mypy_extensions import TypedDict
from typing import Any, Union, List, Dict

from sqlalchemy import Integer, Column, ForeignKey, func, DateTime
from sqlalchemy.orm.session import Session


class SurrogatePK:
    """A mixin that add ``id``、``created_at`` and ``updated_at`` columns
    to any declarative-mapped class.

    **id**: A surrogate integer 'primary key' column.

    **created_at**: Auto save ``datetime.now()`` when row created.

    **updated_at**: Auto save ``datetime.now()`` when row updated.
    """

    __table_args__ = {'extend_existing': True}  # type: ignore

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime, index=True, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, index=True, nullable=False, server_default=func.now(),
        onupdate=func.now())

    __mapper_args__ = {
        'order_by': 'id',
    }

    def __repr__(self) -> str:
        """You can set label property.

        Returns:
            str: ``<{classname}({pk}:{label!r})>``
        """
        return '<{classname}({pk}:{label!r})>'.format(
            classname=type(self).__name__, pk=self.id,
            label=getattr(self, 'label', ''))


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

    See ``sqlalchemy.Column``

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
    """Auto transaction commit or rollback. This worked with
    ``session.autocommit=False`` (the default behavior of ``flask-sqlalchemy``)
    or ``session.autocommit=True``.
    See more: http://flask-sqlalchemy.pocoo.org/2.3/api/#sessions

    Tips:
        * **Can't** do ``session.commit()`` **in func**, **otherwise raise**
          ``sqlalchemy.exc.ResourceClosedError``: `This transaction is closed`.

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
            # db.session.commit() error occurred

    We can nested use this decorator. Must set ``nested=True`` otherwise
    raise ``ResourceClosedError`` (session.autocommit=False) or
    raise ``InvalidRequestError`` (session.autocommit=True)::

        @transaction(db.session, nested=True)
        def set_role(user, role):
            user.role = role
            # db.session.commit() error occurred


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
            if session.autocommit is True and nested is False:
                session.begin()  # start a transaction

            try:
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
