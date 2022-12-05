try:
    from collections import Mapping
except:  # noqa E722
    from collections.abc import Mapping
import inspect
import importlib
import os
import re
import sys
from typing import Any, Dict, List, Optional
from unicodedata import normalize
from distutils.version import LooseVersion
import logging
import datetime

from flask import request
from flask_sqlalchemy import model
from sqlalchemy import UniqueConstraint
import marshmallow
from marshmallow import Schema

from .webargs import use_kwargs as base_use_kwargs, parser

logger = logging.getLogger(__name__)


class ParamsDict(dict):
    """Just available update func.

    Example::

        @use_kwargs(PageParams.update({...}))
        def list_users(page, page_size, order_by):
            pass

    """

    def update(self, other=None):
        """Update self by other Mapping and return self.
        """
        ret = ParamsDict(self.copy())
        if other is not None:
            for k, v in other.items() if isinstance(other, Mapping) else other:
                ret[k] = v
        return ret


class dict2object(dict):
    """Dict to fake object that can use getattr.

    Examples::

        In [2]: obj = dict2object({'a': 2, 'c': 3})

        In [3]: obj.a
        Out[3]: 2

        In [4]: obj.c
        Out[4]: 3

    """

    def __getattr__(self, name: str) -> Any:
        if name in self.keys():
            return self[name]
        raise AttributeError('object has no attribute {}'.format(name))

    def __setattr__(self, name: str, value: Any) -> None:
        if not isinstance(name, str):
            raise TypeError('key must be string type.')
        self[name] = value


def secure_filename(filename: str) -> str:
    """Borrowed from werkzeug.utils.secure_filename.

    Pass it a filename and it will return a secure version of it. This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

        >>> secure_filename(u'哈哈.zip')
        '哈哈.zip'
        >>> secure_filename('My cool movie.mov')
        'My_cool_movie.mov'
        >>> secure_filename('../../../etc/passwd')
        'etc_passwd'
        >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
        'i_contain_cool_umlauts.txt'

    """

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')

    filename = normalize('NFKD', '_'.join(filename.split()))

    filename_strip_re = re.compile(u'[^A-Za-z0-9\u4e00-\u9fa5_.-]')
    filename = filename_strip_re.sub('', filename).strip('._')

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    windows_device_files = (
        'CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
        'LPT2', 'LPT3', 'PRN', 'NUL',
    )
    if os.name == 'nt' and filename and \
            filename.split('.')[0].upper() in windows_device_files:
        filename = '_' + filename

    return filename


def _get_init_args(instance, base_class):
    """Get instance's __init__ args and it's value when __call__.
    """
    getargspec = inspect.getfullargspec
    argspec = getargspec(base_class.__init__)

    defaults = argspec.defaults
    kwargs = {}
    if defaults is not None:
        no_defaults = argspec.args[:-len(defaults)]
        has_defaults = argspec.args[-len(defaults):]

        kwargs = {k: getattr(instance, k) for k in no_defaults
                  if k != 'self' and hasattr(instance, k)}
        kwargs.update({k: getattr(instance, k) if hasattr(instance, k) else
                      getattr(instance, k, defaults[i])
                      for i, k in enumerate(has_defaults)})
        assert len(kwargs) == len(argspec.args) - 1, 'exclude `self`'
    return kwargs


def use_kwargs(argmap, schema_kwargs: Optional[Dict] = None, **kwargs: Any):
    """For fix ``Schema(partial=True)`` not work when used with
    ``@webargs.flaskparser.use_kwargs``. More details ``see webargs.core``.

    Args:

        argmap (marshmallow.Schema,dict,callable): Either a
            `marshmallow.Schema`, `dict` of argname ->
            `marshmallow.fields.Field` pairs, or a callable that returns a
            `marshmallow.Schema` instance.
        schema_kwargs (dict): kwargs for argmap.

    Returns:
        dict: A dictionary of parsed arguments.

    """
    schema_kwargs = schema_kwargs or {}

    argmap = parser._get_schema(argmap, request)

    if not (argmap.partial or schema_kwargs.get('partial')):
        return base_use_kwargs(argmap, **kwargs)

    def factory(request):
        argmap_kwargs = _get_init_args(argmap, Schema)
        argmap_kwargs.update(schema_kwargs)

        # force set force_all=False
        only = parser.parse(argmap, request).keys()

        argmap_kwargs.update({
            'partial': False,  # fix missing=None not work
            'only': only or None,
            'context': {"request": request},
        })
        if tuple(LooseVersion(marshmallow.__version__).version)[0] < 3:
            argmap_kwargs['strict'] = True

        return argmap.__class__(**argmap_kwargs)

    return base_use_kwargs(factory, **kwargs)


def import_subs(locals_, modules_only: bool = False) -> List[str]:
    """ Auto import submodules, used in __init__.py.

    Args:

        locals_: `locals()`.
        modules_only: Only collect modules to __all__.

    Examples::

        # app/models/__init__.py
        from hobbit_core.utils import import_subs

        __all__ = import_subs(locals())

    Auto collect Model's subclass, Schema's subclass and instance.
    Others objects must defined in submodule.__all__.
    """
    package = locals_['__package__']
    path = locals_['__path__']
    top_mudule = sys.modules[package]

    all_ = []
    for name in os.listdir(path[0]):
        if not name.endswith(('.py', '.pyc')) or name.startswith('__init__.'):
            continue

        module_name = name.split('.')[0]
        submodule = importlib.import_module(f".{module_name}", package)
        all_.append(module_name)

        if modules_only:
            continue

        if hasattr(submodule, '__all__'):
            for name in getattr(submodule, '__all__'):
                if not isinstance(name, str):
                    raise Exception(f'Invalid object {name} in __all__, '
                                    f'must contain only strings.')
                setattr(top_mudule, name, getattr(submodule, name))
                all_.append(name)
        else:
            for name, obj in submodule.__dict__.items():
                if isinstance(obj, (model.DefaultMeta, Schema)) or \
                        (inspect.isclass(obj) and
                         (issubclass(obj, Schema) or
                          obj.__name__.endswith('Service'))):
                    setattr(top_mudule, name, obj)
                    all_.append(name)
    return all_


def bulk_create_or_update_on_duplicate(
        db, model_cls, items, updated_at='updated_at', batch_size=500):
    """ Support MySQL and postgreSQL.
    https://dev.mysql.com/doc/refman/8.0/en/insert-on-duplicate.html

    Args:

        db: Instance of `SQLAlchemy`.
        model_cls: Model object.
        items: List of data,[ example: `[{key: value}, {key: value}, ...]`.
        updated_at: Field which recording row update time.
        batch_size: Batch size is max rows per execute.

    Returns:
        dict: A dictionary contains rowcount and items_count.
    """
    if not items:
        logger.warning("bulk_create_or_update_on_duplicate save to "
                       f"{model_cls} failed, empty items")
        return {'rowcount': 0, 'items_count': 0}

    items_count = len(items)
    table_name = model_cls.__tablename__
    fields = list(items[0].keys())
    unique_keys = [c.name for i in model_cls.__table_args__ if isinstance(
        i, UniqueConstraint) for c in i]
    columns = [c.name for c in model_cls.__table__.columns if c.name not in (
        'id', 'created_at')]

    if updated_at in columns and updated_at not in fields:
        fields.append(updated_at)
        updated_at_time = datetime.datetime.now()
        for item in items:
            item[updated_at] = updated_at_time

    assert set(fields) == set(columns), \
        'item fields not equal to columns in models：new: ' + \
        f'{set(fields)-set(columns)}, delete: {set(columns)-set(fields)}'

    for item in items:
        for column in unique_keys:
            if column in item and item[column] is None:
                item[column] = ''

    engine = db.get_engine(bind_key=getattr(model_cls, '__bind_key__', None))
    if engine.name == 'postgresql':
        sql_on_update = ', '.join([
            f' {field} = excluded.{field}'
            for field in fields if field not in unique_keys])
        sql = f"""INSERT INTO {table_name} ({", ".join(fields)}) VALUES
            ({", ".join([f':{key}' for key in fields])})
            ON CONFLICT ({", ".join(unique_keys)}) DO UPDATE SET
            {sql_on_update}"""
    elif engine.name == 'mysql':
        sql_on_update = '`, `'.join([
            f' `{field}` = new.{field}' for field in fields
            if field not in unique_keys])
        sql = f"""INSERT INTO {table_name} (`{"`, `".join(fields)}`) VALUES
            ({", ".join([f':{key}' for key in fields])}) AS new
            ON DUPLICATE KEY UPDATE
            {sql_on_update}"""
    else:
        raise Exception(f'not support db: {engine.name}')

    rowcounts = 0
    while len(items) > 0:
        batch, items = items[:batch_size], items[batch_size:]
        try:
            result = db.session.execute(sql, batch, bind=engine)
        except Exception as e:
            logger.error(e, exc_info=True)
            logger.info(sql)
            raise e
        rowcounts += result.rowcount
    logger.info(f'{model_cls} save_data: rowcount={rowcounts}, '
                f'items_count: {items_count}')
    return {'rowcount': rowcounts, 'items_count': items_count}
