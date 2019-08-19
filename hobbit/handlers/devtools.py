import os
import sys
from subprocess import run, PIPE, STDOUT

import click

from hobbit import ROOT_PATH


def dev_init(all_, hooks, pipenv):
    run('git init', shell=True)

    if all_ or hooks:
        HOOKS_PATH = os.path.join(ROOT_PATH, 'static', 'hooks')
        run(f'cp -r {HOOKS_PATH}/* .git/hooks', shell=True)

    if all_ or pipenv:
        sub = run('which pipenv', shell=True, stdout=PIPE, stderr=STDOUT)
        if sub.returncode != 0:
            click.echo(click.style('cmd pipenv not exist.', fg='red'))
            sys.exit(sub.returncode)
        pipenv_path = sub.stdout.strip().decode('utf8')

        pipenv_cmds = [
            f'{pipenv_path} install --dev pytest pytest-cov pytest-env flake8',
        ]
        if 'requirements.txt' in os.listdir():
            pipenv_cmds.insert(
                0, f'{pipenv_path} install -r requirements.txt --pre')

        cmd = ' && '.join(pipenv_cmds)
        click.echo(click.style(cmd, fg='green'))
        # force pipenv to ignore that environment and create its own instead
        env = os.environ.copy()
        env.update({'PIPENV_IGNORE_VIRTUALENVS': '1'})
        run(cmd, shell=True, env=env)
