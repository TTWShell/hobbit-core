import os

import click

from .handlers import echo
from .handlers.bootstrap import render_project


@click.group()
@click.pass_context
def cli(ctx, force):
    pass


@cli.command()
@click.option('-n', '--name', help='Name of project.', required=True)
@click.option('-d', '--dist', type=click.Path(), default='.',
              help='Dir for new project.')
@click.option('-t', '--template', type=click.Choice(['shire']),
              default='shire', help='Template name.')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Force render files, covered if file exist.')
@click.pass_context
def startproject(ctx, name, dist, template, force):
    """Create a new flask project, render from different template.
    """
    ctx.obj['FORCE'] = force
    ctx.obj['JINJIA_CONTEXT'] = {
        'project_name': name,
    }

    echo('Start init a hobbit project `{}` to `{}`, use template {}',
         (name, dist, template))

    tpl_path = os.path.join(
        os.path.split(os.path.abspath(__name__))[0],
        'hobbit_core', 'hobbit', 'static', 'bootstrap', template)
    if not os.path.exists(tpl_path):
        raise click.UsageError(
            click.style('Tpl `{}` not exists.'.format(template), fg='red'))

    render_project(dist, tpl_path)

    echo('project `{}` render finished.', (name, ))


CMDS = [startproject]
