import os
import random
import string

import click

from hobbit_core import VERSION

from .handlers import echo
from .handlers.bootstrap import render_project


@click.group()
@click.pass_context
def cli(ctx, force):
    pass


@cli.command()
@click.option('-n', '--name', help='Name of project.', required=True)
@click.option('-p', '--port', help='Port of web server.', required=True,
              type=click.IntRange(1024, 65535))
@click.option('-d', '--dist', type=click.Path(), required=False,
              help='Dir for new project.')
@click.option('-t', '--template', type=click.Choice(['shire', 'expirement']),
              default='shire', help='Template name.')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Force render files, covered if file exist.')
@click.option('--celery/--no-celery', default=False,
              help='Generate celery files or not.')
@click.pass_context
def startproject(ctx, name, port, dist, template, force, celery):
    """Create a new flask project, render from different template.

    Examples::

        hobbit --echo startproject -n demo -d /tmp/test -p 1024

    Other tips::

        hobbit --help
    """
    dist = os.getcwd() if dist is None else os.path.abspath(dist)
    ctx.obj['FORCE'] = force
    ctx.obj['CELERY'] = celery
    ctx.obj['JINJIA_CONTEXT'] = {
        'project_name': name,
        'port': port,
        'secret_key': ''.join(random.choice(
            string.ascii_letters) for i in range(38)),
        'version': '.'.join(str(i) for i in VERSION),
        'celery': celery,
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


@cli.command()
@click.option('-n', '--name', help='Name of feature.', required=True)
@click.option('-d', '--dist', type=click.Path(), required=False,
              help='Dir for new project.')
@click.pass_context
def gen(ctx, name, dist):
    """Generator models/{name}.py, schemas/{name}.py, views/{name}.py etc.
    """
    dist = os.getcwd() if dist is None else os.path.abspath(dist)

    ctx.obj['FORCE'] = False
    ctx.obj['JINJIA_CONTEXT'] = {'name': name}

    tpl_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static', 'bootstrap', 'feature')

    render_project(dist, tpl_path)


CMDS = [startproject, gen]
