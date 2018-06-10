from contextlib import contextmanager
import os

import click
from jinja2 import Environment, FileSystemLoader, Template
from . import echo

SUFFIX = '.jinjia2'


@contextmanager
def chdir(dist):
    cwd = os.getcwd()
    echo('mkdir {}', (dist, ))
    os.makedirs(dist, exist_ok=True)
    os.chdir(dist)
    yield dist
    os.chdir(cwd)


@click.pass_context
def render_project(ctx, dist, tpl_path):
    jinjia_env = Environment(loader=FileSystemLoader(tpl_path))
    with chdir(dist):
        for fn in os.listdir(tpl_path):
            origin_path = os.path.join(tpl_path, fn)
            if os.path.isdir(origin_path):
                dir_name = Template(fn).render(ctx.obj['JINJIA_CONTEXT'])[:-8] \
                    if fn.endswith(SUFFIX) else fn
                render_project(os.path.join(dist, dir_name),
                               os.path.join(tpl_path, fn))
                continue

            if os.path.isfile(origin_path) and not fn.endswith(SUFFIX):
                raise click.ClickException(click.style(
                    'FileTypeError: tpl must endswith `{}`. '
                    'File is {}'.format(
                        SUFFIX, os.path.join(tpl_path, fn)), fg='red'))

            data = jinjia_env.get_template(fn).render(
                ctx.obj['JINJIA_CONTEXT'])
            render_file(dist, fn[:-8], data)


@click.pass_context
def render_file(ctx, dist, fn, data):
    if os.path.isfile(fn) and not ctx.obj['FORCE']:
        echo('exists {}, ignore ...'.format(fn))
        return

    echo('render {} ...', (os.path.join(dist, fn), ))

    with open(fn, 'w') as wf:
        wf.write(data)
