# -*- encoding: utf-8 -*-
import enum

from sqlalchemy import Integer, Column, ForeignKey, func, DateTime


class SurrogatePK(object):
    """A mixin that add ``id``、``created_at`` and ``updated_at`` columns
    to any declarative-mapped class.

    **id**: A surrogate integer 'primary key' column.

    **created_at**: Auto save ``datetime.now()`` when row created.

    **updated_at**: Auto save ``datetime.now()`` when row updated.
    """

    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        onupdate=func.now())

    def __repr__(self):
        """You can set label property.

        Returns:
            str: ``<{classname}({pk}:{label!r})>``
        """
        return '<{classname}({pk}:{label!r})>'.format(
            classname=type(self).__name__, pk=self.id,
            label=getattr(self, 'label', ''))


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Args:
        tablename (str): Model.__table_name__.
        nullable (bool): Default is False.
        pk_name (str): Primary column's name.

    Others:

    See ``sqlalchemy.Column``

    Examples::

        from sqlalchemy.orm import relationship

        role_id = reference_col('role')
        role = relationship('Role', backref='users', cascade='all, delete')
    """

    return Column(
        ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class EnumExt(enum.Enum):
    """
    TODO:
        * extension.
    """
    pass
