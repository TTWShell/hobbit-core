import os
import random
import string

import click

from .handlers import echo
from .handlers.bootstrap import render_project
from hobbit_core import VERSION


@click.group()
@click.pass_context
def cli(ctx, force):
    pass


@cli.command()
@click.option('-n', '--name', help='Name of project.', required=True)
@click.option('-d', '--dist', type=click.Path(), required=False,
              help='Dir for new project.')
@click.option('-t', '--template', type=click.Choice(['shire']),
              default='shire', help='Template name.')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Force render files, covered if file exist.')
@click.pass_context
def startproject(ctx, name, dist, template, force):
    """Create a new flask project, render from different template.

    Examples::

        hobbit --echo startproject -n demo -d /tmp/test

    Proj tree::

        .
        ├── demo
        │   ├── __init__.py
        │   ├── config.py
        │   ├── exts.py
        │   ├── models
        │   │   ├── __init__.py
        │   │   └── example.py
        │   ├── run.py
        │   ├── schemas
        │   │   ├── __init__.py
        │   │   └── example.py
        │   ├── utils.py
        │   └── views
        │       ├── __init__.py
        │       └── example.py
        ├── docs
        ├── requirements.txt
        └── tests
            ├── __init__.py
            ├── conftest.py
            └── test_example.py

    Other tips::

        hobbit --help
    """
    dist = os.getcwd() if dist is None else dist
    ctx.obj['FORCE'] = force
    ctx.obj['JINJIA_CONTEXT'] = {
        'project_name': name,
        'secret_key': ''.join(random.choice(
            string.ascii_letters) for i in range(38)),
        'version': '.'.join(str(i) for i in VERSION),
    }

    echo('Start init a hobbit project `{}` to `{}`, use template {}',
         (name, dist, template))

    tpl_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static', 'bootstrap', template)
    if not os.path.exists(tpl_path):
        raise click.UsageError(
            click.style('Tpl `{}` not exists.'.format(template), fg='red'))

    render_project(dist, tpl_path)

    echo('project `{}` render finished.', (name, ))


CMDS = [startproject]
