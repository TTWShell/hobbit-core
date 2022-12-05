from contextlib import contextmanager
import os
import re

import click
from jinja2 import Environment, FileSystemLoader, Template

from . import echo

SUFFIX = '.jinja2'


def regex_replace(s, find, replace):
    """A non-optimal implementation of a regex filter"""
    return re.sub(find, replace, s)


@contextmanager
def chdir(dist):
    cwd = os.getcwd()
    # exist_ok py3 only
    if not os.path.exists(dist):
        echo(f'mkdir\t{dist}')
        os.makedirs(dist)
    os.chdir(dist)
    yield dist
    os.chdir(cwd)


@click.pass_context
def render_project(ctx, dist, tpl_path):
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

            dir_name = Template(fn).render(context)
            render_project(os.path.join(dist, dir_name),
                           os.path.join(tpl_path, fn))


@click.pass_context
def render_file(ctx, dist, fn, data):
    target = os.path.join(dist, fn)
    if os.path.isfile(fn) and not ctx.obj['FORCE']:
        echo(f'exists {target}, ignore ...')
        return

    echo(f'render\t{target} ...')

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
            click.style(f'Tpl `{value}` not exists.', fg='red'))

    return tpl_path
