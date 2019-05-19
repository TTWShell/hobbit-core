from collections import namedtuple, defaultdict
from contextlib import contextmanager
import csv
import os
import re

import click
from jinja2 import Environment, FileSystemLoader, Template

from hobbit import inflect_engine

SUFFIX = '.jinja2'
Column = namedtuple('Column', [
    'field', 'type', 'type_arg', 'is_unique', 'is_index', 'is_null', 'doc', 'test'])

""" Gen types
from sqlalchemy import types
from sqlalchemy.sql.visitors import VisitableType

[
    k for k, v in types.__dict__.items()
    if isinstance(v, VisitableType) and k != k.upper()
    and not k.startswith('_')]
"""
ORM_TYPES = [
    'BigInteger',
    'Binary',
    'Boolean',
    'Date',
    'DateTime',
    'Enum',
    'Float',
    'Integer',
    'Interval',
    'LargeBinary',
    'MatchType',
    'NullType',
    'Numeric',
    'PickleType',
    'SmallInteger',
    'String',
    'Text',
    'Time',
    'Unicode',
    'UnicodeText',
]
ORM_TYPE_MAPS = {t.lower(): t for t in ORM_TYPES}


def regex_replace(s, find, replace):
    """A non-optimal implementation of a regex filter"""
    return re.sub(find, replace, s)


@click.pass_context
def echo(ctx, msg, args=None):
    if not ctx.obj['ECHO']:
        return

    if args:
        click.echo(msg.format(*args))
    else:
        click.echo(msg)


@contextmanager
def chdir(dist):
    cwd = os.getcwd()
    # exist_ok py3 only
    if not os.path.exists(dist):
        echo('mkdir\t{}', (dist, ))
        os.makedirs(dist)
    os.chdir(dist)
    yield dist
    os.chdir(cwd)


@click.pass_context
def render_project(ctx, dist, tpl_path):
    celery = ctx.obj.get('CELERY')  # gen cmd not have this arg
    context = ctx.obj['JINJIA_CONTEXT']

    jinjia_env = Environment(loader=FileSystemLoader(tpl_path))
    jinjia_env.filters['regex_replace'] = regex_replace

    with chdir(dist):
        for fn in os.listdir(tpl_path):
            origin_path = os.path.join(tpl_path, fn)

            if os.path.isfile(origin_path) and not fn.endswith(SUFFIX):
                continue

            if os.path.isfile(origin_path):
                data = jinjia_env.get_template(fn).render(context)
                fn = Template(fn).render(context)
                render_file(dist, fn[:-len(SUFFIX)], data)
                continue

            if not celery and origin_path.endswith('tasks'):
                continue

            dir_name = Template(fn).render(context)
            render_project(os.path.join(dist, dir_name),
                           os.path.join(tpl_path, fn))


@click.pass_context
def render_file(ctx, dist, fn, data):
    target = os.path.join(dist, fn)
    if os.path.isfile(fn) and not ctx.obj['FORCE']:
        echo('exists {}, ignore ...', (target, ))
        return

    echo('render\t{} ...', (target, ))

    with open(fn, 'w') as wf:
        wf.write(data)

    if fn.endswith('.sh'):
        os.chmod(fn, 0o755)


def validate_template_path(ctx, param, value):
    from hobbit import ROOT_PATH
    dir = 'feature' if ctx.command.name == 'gen' else 'bootstrap'
    tpl_path = os.path.join(ROOT_PATH, 'static', dir, value)

    if not os.path.exists(tpl_path):
        raise click.UsageError(
            click.style('Tpl `{}` not exists.'.format(value), fg='red'))

    return tpl_path


def gen_metadata_by_name(name):
    module = '_'.join(name.split('_')).lower()
    model = ''.join([sub.capitalize() for sub in name.split('_')])

    if module != name or not all(name.split('_')):
        raise click.UsageError(click.style(
            f'Name `{name}` should be lowercase, with words separated by '
            f'underscores as necessary to improve readability.', fg='red'))

    return module, model


def cleaning_test_value(type_, value):
    if type_ in ['BigInteger', 'Float', 'Integer', 'SmallInteger']:
        return value
    if type_ == 'Boolean':
        return value.capitalize()
    return f"'{value}'"


def gen_column(row):
    column = Column(*row)

    gen_metadata_by_name(column.field)  # validate the field name

    assert column.type.lower() in ORM_TYPE_MAPS, \
        f'column type err: cannot be `{column.type}`'

    type_ = ORM_TYPE_MAPS[column.type.lower()]
    is_unique = True if column.is_unique else False
    is_index = True if column.is_index else False
    is_null = True if column.is_null else False
    test = cleaning_test_value(type_, column.test)

    column = column._replace(
        type=type_, is_null=str(is_null),
        is_unique=str(is_unique), is_index=str(is_index), test=test)

    return column


def gen_model():
    class Model:
        singular = None
        plural = None
        columns = []
    return Model


def validate_csv_file(ctx, param, value):
    model, data = None, defaultdict(gen_model)
    if value is None:
        return data
    with open(value) as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            if spamreader.line_num == 1:
                continue
            if len(row) == 1 or row[0] == ''.join(row):
                module, model = gen_metadata_by_name(row[0])
                data[model].singular = module
                data[model].plural = inflect_engine.plural(module)
            elif len(row) == 8:
                data[model].columns.append(gen_column(row))
            else:
                raise click.UsageError(
                    click.style(f'csv file err: `{row}`.', fg='red'))
    return data
