import os
import click
from subprocess import run

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
@click.pass_context
def init(ctx):
    """Init dev env: git hooks, pyenv install etc.
    """
    run('git init', shell=True)

    HOOKS_PATH = os.path.join(ROOT_PATH, 'static', 'hooks')
    run(f'cp -r {HOOKS_PATH}/* .git/hooks', shell=True)

    pipenv_cmds = [
        'pipenv install --dev pytest pytest-cov pytest-env flake8',
        'pipenv shell',
    ]
    if 'requirements.txt' in os.listdir():
        pipenv_cmds.insert(0, 'pipenv install -r requirements.txt --pre')

    cmd = ' && '.join(pipenv_cmds)
    # force pipenv to ignore that environment and create its own instead
    run(cmd, shell=True, env={'PIPENV_IGNORE_VIRTUALENVS': '1'})
