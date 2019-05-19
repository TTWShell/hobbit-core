import os
import random
import string
import pkg_resources

import click

from .handlers.bootstrap import echo, render_project, gen_metadata_by_name, \
    validate_template_path, validate_csv_file
from . import HobbitCommand, inflect_engine

templates = ['shire', 'expirement']


@click.group()
@click.pass_context
def cli(ctx, force):
    pass


@cli.command(cls=HobbitCommand)
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
def new(ctx, name, port, dist, template, force, celery):
    """Create a new flask project, render from different template.

    Examples::

        hobbit --echo new -n demo -d /tmp/test -p 1024

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


@cli.command(cls=HobbitCommand)
@click.option('-n', '--name', help='Name of feature.', required=True)
@click.option('-d', '--dist', type=click.Path(), required=False,
              help='Dir for new feature.')
@click.option('-t', '--template', type=click.Choice(templates),
              default='shire', callback=validate_template_path,
              help='Template name.')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Force render files, covered if file exist.')
@click.option('-c', '--csv-path', required=False, type=click.Path(exists=True),
              callback=validate_csv_file,
              help='A csv file that defines some models.')
@click.pass_context
def gen(ctx, name, template, dist, force, csv_path):
    """Generator new feature. Auto gen models/{name}.py, schemas/{name}.py,
    views/{name}.py, services/{name.py}, tests/test_{name}.py etc.
    """
    dist = os.getcwd() if dist is None else os.path.abspath(dist)
    module, model = gen_metadata_by_name(name)
    if not csv_path:
        # default gen username column
        from hobbit.handlers.bootstrap import gen_column
        csv_path[model].singular = module
        csv_path[model].plural = inflect_engine.plural(module)
        csv_path[model].columns.append(gen_column([
            'username', 'String', 20, '', 'index', '', '用户名', 'test']))

    ctx.obj['FORCE'] = force
    ctx.obj['JINJIA_CONTEXT'] = {
        'name': name,
        'module': module,
        'metadata': csv_path,  # auto read data when validate
    }

    render_project(dist, template)


CMDS = [new, gen]
