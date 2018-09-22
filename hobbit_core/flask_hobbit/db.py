import enum

from sqlalchemy import Integer, Column, ForeignKey, func, DateTime


class SurrogatePK:
    """Base model."""
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        onupdate=func.now())

    def __repr__(self):
        return '<{classname}({pk}:{label!r})>'.format(
            classname=type(self).__name__, pk=self.id, label=self.label or '')


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    return Column(
        ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class EnumExt(enum.Enum):
    pass
