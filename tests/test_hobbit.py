import os
import subprocess
import itertools

import pytest
from click.testing import CliRunner

from hobbit import main as hobbit
from hobbit.bootstrap import templates

from . import BaseTest, rmdir, chdir


class TestHobbit(BaseTest):
    wkdir = os.path.abspath('hobbit-tox-test')

    def setup_method(self, method):
        rmdir(self.wkdir)

    def teardown_method(self, method):
        os.chdir(self.root_path)
        rmdir(self.wkdir)

    @pytest.fixture
    def runner(self):
        yield CliRunner()

    def test_not_exist_cmd(self, runner):
        result = runner.invoke(hobbit)
        assert result.exit_code == 0

        result = runner.invoke(hobbit, ['doesnotexistcmd'], obj={})
        assert 'Error: cmd not exist: doesnotexistcmd' in result.output

    @pytest.mark.parametrize(
        'name,template,celery_,dist',
        itertools.product(
            ['haha'], templates, ['--celery', '--no-celery'],
            [None, '.', wkdir]))
    @chdir(wkdir)
    def test_new_cmd(self, runner, name, template, celery_, dist):
        options = [
            '--echo', 'new', '-p 1024', '-n', name,  '-t', template, celery_]
        if dist:
            assert os.getcwd() == os.path.abspath(dist)
            options.extend(['-d', dist])

        result = runner.invoke(hobbit, options, obj={})
        assert result.exit_code == 0, result.output
        assert 'mkdir\t{}'.format(self.wkdir) in result.output
        assert 'render\t{}'.format(self.wkdir) in result.output

        file_nums = {
            # tart + 29 files + 11 dir + 1 end + empty
            'shire | --no-celery':  1 + 29 + 11 + 1 + 1 - 1,
            # start + files + mkdir + tail
            'shire | --celery': 1 + 30 + 12 + 1,
            'rivendell | --no-celery':  1 + 31 + 11 + 1,
            'rivendell | --celery':  1 + 32 + 12 + 1,
        }
        assert len(result.output.split('\n')) == file_nums[
            f'{template} | {celery_}']

        assert subprocess.call(['flake8', '.']) == 0
        assert subprocess.call(
            'pip install -r requirements.txt '
            '--upgrade-strategy=only-if-needed',
            shell=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL) == 0
        assert subprocess.call(['pytest'], stdout=subprocess.DEVNULL) == 0

        # test --force option
        result = runner.invoke(hobbit, options, obj={})
        assert all([i in result.output for i in ['exists ', 'ignore ...']])
        options.extend(['-f'])
        result = runner.invoke(hobbit, options, obj={})
        assert any([i in result.output for i in ['exists ', 'ignore ...']])

    @pytest.fixture
    def csv_file(self, runner):
        cmd = ['create', '-n', 'tests/models.csv']
        result = runner.invoke(hobbit, cmd, obj={})
        assert result.exit_code == 0

    @pytest.mark.parametrize("gen_cmd", [
        ['--echo', 'gen', '-n', 'user', '-t', 'rivendell'],
        ['--echo', 'gen', '-n', 'user', '-t', 'rivendell', '-f', '--csv-path',
         os.path.join(BaseTest.root_path, 'tests', 'models.csv')],
    ])
    @chdir(wkdir)
    def test_new_rivendell_tpl_and_gen_cmd(self, runner, gen_cmd, csv_file):
        assert os.getcwd() == self.wkdir

        # new project use rivendell template
        cmd = [
            '--echo', 'new', '-n', 'haha', '-p', '1024',
            '-t', 'rivendell']
        result = runner.invoke(hobbit, cmd, obj={})
        # start + files + mkdir + tail
        assert result.exit_code == 0

        # gen new module
        result = runner.invoke(hobbit, gen_cmd, obj={})
        assert result.exit_code == 0
        assert len(result.output.split('\n')) == 5 + 1, result.output  # files

        # flake8 check
        assert subprocess.call(['flake8', '.']) == 0
        # pytest
        assert subprocess.call(
            ['pytest', '--no-cov'], stdout=subprocess.DEVNULL) == 0
