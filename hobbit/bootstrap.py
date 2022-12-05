import os
import random
import string
import pkg_resources

import click

from .handlers import echo
from .handlers.bootstrap import render_project, validate_template_path
from . import HobbitCommand, HobbitGroup, CONTEXT_SETTINGS

templates = ['shire', 'rivendell']


@click.group(cls=HobbitGroup, context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def common_options(func):
    func = click.option(
        '-f', '--force', default=False, is_flag=True,
        help='Covered if file exist.')(func)
    func = click.option(
        '-t', '--template', type=click.Choice(templates),
        default='shire', callback=validate_template_path,
        help='Template name.')(func)
    func = click.option(
        '-d', '--dist', type=click.Path(), required=False,
        help='Target path.')(func)
    return func


@cli.command(cls=HobbitCommand)
@click.option('-n', '--name', help='Name of project.', required=True)
@click.option('-p', '--port', help='Port of web server.', required=True,
              type=click.IntRange(1024, 65535))
@common_options
@click.pass_context
def new(ctx, name, port, dist, template, force):
    """Create a new flask project, render from different template.

    Examples::

        hobbit --echo new -n blog -d /tmp/test -p 1024

    It is recommended to use pipenv to create venv::

        pipenv install -r requirements.txt && pipenv install --dev pytest pytest-cov pytest-env ipython flake8 ipdb
    """  # noqa
    dist = os.getcwd() if dist is None else os.path.abspath(dist)
    ctx.obj['FORCE'] = force
    ctx.obj['JINJIA_CONTEXT'] = {
        'project_name': name,
        'port': port,
        'secret_key': ''.join(random.choice(
            string.ascii_letters) for i in range(38)),
        'version': pkg_resources.get_distribution("hobbit-core").version,
    }

    echo(f'Start init a hobbit project `{name}` to `{dist}`,'
         f' use template {template}')
    render_project(dist, template)
    echo(f'project `{name}` render finished.')


cmd_list = [new]
