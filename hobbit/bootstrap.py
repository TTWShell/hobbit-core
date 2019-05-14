import os
import random
import string
import pkg_resources

import click
import inflect

from .handlers import echo
from .handlers.bootstrap import render_project

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
engine = inflect.engine()
templates = ['shire', 'expirement']


def validate_template_path(ctx, param, value):
    dir = 'feature' if ctx.command.name == 'gen' else 'bootstrap'
    tpl_path = os.path.join(ROOT_PATH, 'static', dir, value)

    if not os.path.exists(tpl_path):
        raise click.UsageError(
            click.style('Tpl `{}` not exists.'.format(value), fg='red'))

    return tpl_path


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
@click.option('-t', '--template', type=click.Choice(templates),
              default='shire', callback=validate_template_path,
              help='Template name.')
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
        'version': pkg_resources.get_distribution("hobbit-core").version,
        'celery': celery,
    }

    echo('Start init a hobbit project `{}` to `{}`, use template {}',
         (name, dist, template))
    render_project(dist, template)
    echo('project `{}` render finished.', (name, ))


@cli.command()
@click.option('-n', '--name', help='Name of feature.', required=True)
@click.option('-d', '--dist', type=click.Path(), required=False,
              help='Dir for new feature.')
@click.option('-t', '--template', type=click.Choice(templates),
              default='shire', callback=validate_template_path,
              help='Template name.')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Force render files, covered if file exist.')
@click.pass_context
def gen(ctx, name, template, dist, force):
    """Generator new feature. Auto gen models/{name}.py, schemas/{name}.py,
    views/{name}.py, services/{name.py}, tests/test_{name}.py etc.
    """
    dist = os.getcwd() if dist is None else os.path.abspath(dist)
    module = '_'.join(name.split('_')).lower()
    model = ''.join([sub.capitalize() for sub in name.split('_')])

    if module != name or not all(name.split('_')):
        raise click.UsageError(click.style(
            'name should be lowercase, with words separated by '
            'underscores as necessary to improve readability.', fg='red'))

    ctx.obj['FORCE'] = force
    ctx.obj['JINJIA_CONTEXT'] = {
        'name': name,
        'module': module,
        'model': model,
        'plural': engine.plural(module)
    }

    render_project(dist, template)


CMDS = [startproject, gen]
