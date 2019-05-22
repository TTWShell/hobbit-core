import os
import random
import string
import pkg_resources

import click

from .handlers.bootstrap import echo, render_project, gen_metadata_by_name, \
    validate_template_path, validate_csv_file, MetaModel, create_models_csv
from . import HobbitCommand, main as cli

templates = ['shire', 'expirement']


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
@click.option('--celery/--no-celery', default=False,
              help='Generate celery files or not.')
@click.pass_context
def new(ctx, name, port, dist, template, force, celery):
    """Create a new flask project, render from different template.

    Examples::

        hobbit --echo new -n blog -d /tmp/test -p 1024

    It is recommended to use pipenv to create venv::

        pipenv install -r requirements.txt && pipenv install --dev pytest pytest-cov pytest-env ipython flake8 ipdb
    """  # noqa
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

    echo(f'Start init a hobbit project `{name}` to `{dist}`,'
         f' use template {template}')
    render_project(dist, template)
    echo(f'project `{name}` render finished.')


@cli.command(cls=HobbitCommand)
@click.option('-n', '--name', help='Name of feature.', required=True)
@common_options
@click.option('-c', '--csv-path', required=False, type=click.Path(exists=True),
              callback=validate_csv_file,
              help='A csv file that defines some models.')
@click.pass_context
def gen(ctx, name, template, dist, force, csv_path):
    """Generator new feature. Auto gen models/{name}.py, schemas/{name}.py,
    views/{name}.py, services/{name.py}, tests/test_{name}.py etc.
    """
    dist = os.getcwd() if dist is None else os.path.abspath(dist)
    module, _ = gen_metadata_by_name(name)

    if csv_path:
        metadata = {m.name: m for m in MetaModel.csv2model(csv_path)}
    else:
        default = MetaModel.gen_default(name)
        metadata = {default.name: default}

    ctx.obj['FORCE'] = force
    ctx.obj['JINJIA_CONTEXT'] = {
        'name': name,
        'module': module,
        'metadata': metadata,
    }

    render_project(dist, template)


@cli.command(
    cls=HobbitCommand,
    short_help='Create {name}.csv file for gen --csv-path option.',
    help=f"""Create {{name}}.csv file for gen --csv-path option.

    Support type:

        {', '.join(MetaModel.ORM_TYPES + [MetaModel.TYPE_REF])}

    ref type (hobbit_core.db.reference_col) used for ForeignKey.
    """
)
@click.option('-n', '--name', help='Name of csv file.', required=True)
@click.pass_context
def create(ctx, name):
    create_models_csv(name)


CMDS = [new, gen, create]
