import os
import click
from subprocess import run

from .handlers import echo
from . import HobbitGroup, CONTEXT_SETTINGS, ROOT_PATH


class BootstrapGroup(HobbitGroup):

    @property
    def cmds(self):
        return {func.name: func for func in [init]}


@click.group(cls=BootstrapGroup, context_settings=CONTEXT_SETTINGS)
def dev():
    """Dev tools, more: hobbit dev --help.
    """
    pass


@dev.command()
@click.option('-a', '--all', 'all_', default=False, is_flag=True,
              help='Run all.')
@click.option('--hooks', default=False, is_flag=True, help='Install hooks.')
@click.option('--pipenv', default=False, is_flag=True,
              help='Create virtualenv by pipenv.')
@click.pass_context
def init(ctx, all_, hooks, pipenv):
    """Init dev env: git hooks, pyenv install etc.
    """
    run('git init', shell=True)

    if all_ or hooks:
        HOOKS_PATH = os.path.join(ROOT_PATH, 'static', 'hooks')
        run(f'cp -r {HOOKS_PATH}/* .git/hooks', shell=True)

    pipenv_cmds = [
        'pipenv install --dev pytest pytest-cov pytest-env flake8',
    ]
    if 'requirements.txt' in os.listdir():
        pipenv_cmds.insert(0, 'pipenv install -r requirements.txt --pre')

    cmd = ' && '.join(pipenv_cmds)
    # force pipenv to ignore that environment and create its own instead
    if all_ or pipenv:
        run(cmd, shell=True)
        echo('Please run: pipenv shell')
