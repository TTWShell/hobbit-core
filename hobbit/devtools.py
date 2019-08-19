import click

from . import HobbitGroup, CONTEXT_SETTINGS
from .handlers.devtools import dev_init


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
    dev_init(all_, hooks, pipenv)
