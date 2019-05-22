import os
from subprocess import call

import pytest
from click.testing import CliRunner

from hobbit import main as hobbit

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

    def test_hobbit_cmd(self, runner):
        result = runner.invoke(hobbit)
        assert result.exit_code == 0

        result = runner.invoke(hobbit, ['doesnotexistcmd'], obj={})
        assert 'Error: cmd not exist: doesnotexistcmd' in result.output

    @chdir(wkdir)
    def test_new_cmd_nodist(self, runner):
        assert os.getcwd() == self.wkdir

        result = runner.invoke(hobbit, ['--echo', 'new'], obj={})
        assert result.exit_code == 2
        assert 'Error: Missing option "-n" / "--name".' in result.output

        result = runner.invoke(
            hobbit, [
                '--echo', 'new', '-n', 'haha', '-f', '-p', '1024',
            ], obj={})
        assert result.exit_code == 0
        assert 'mkdir\t{}'.format(self.wkdir) in result.output
        assert 'render\t{}'.format(self.wkdir) in result.output
        assert os.path.exists(os.path.join(
            os.getcwd(), 'app', 'models', '__init__.py'))
        assert 'example.py' not in result.output

    def test_new_cmd_dist(self, runner):
        result = runner.invoke(
            hobbit, [
                '--echo', 'new', '-n', 'haha', '-f', '-d', self.wkdir,
                '-p', '1024',
            ], obj={})
        assert result.exit_code == 0
        assert 'mkdir\t{}'.format(self.wkdir) in result.output
        assert 'render\t{}'.format(self.wkdir) in result.output
        assert os.path.exists(os.path.join(
            self.wkdir, 'app', 'models', '__init__.py'))
        assert 'example.py' not in result.output

    @chdir(wkdir)
    def test_new_cmd_curdir(self, runner):
        assert os.getcwd() == self.wkdir

        result = runner.invoke(
            hobbit, [
                '--echo', 'new', '-n', 'haha', '-f', '-d', '.',
                '-p', '1024',
            ], obj={})
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(
            os.getcwd(), 'app', 'models', '__init__.py'))
        assert 'example.py' not in result.output

    @chdir(wkdir)
    def test_new_cmd(self, runner):
        assert os.getcwd() == self.wkdir

        cmd = [
            '--echo', 'new', '-n', 'haha', '-p', '1024']
        result = runner.invoke(hobbit, cmd, obj={})
        # start + 29 files + 11 dir + 1 end + empty
        # in this test case. main dir exists, so mkdir - 1
        assert len(result.output.split('\n')) == 1 + 29 + 11 + 1 + 1 - 1
        assert result.exit_code == 0

        # test no -f worked
        result = runner.invoke(hobbit, cmd, obj={})
        assert result.exit_code == 0
        assert ', ignore' in result.output
        assert call(['flake8', '.']) == 0

    @chdir(wkdir)
    def test_new_cmd_celery(self, runner):
        assert os.getcwd() == self.wkdir

        cmd = [
            '--echo', 'new', '-n', 'haha', '-p', '1024',
            '--celery']
        result = runner.invoke(hobbit, cmd, obj={})
        # start + files + mkdir + tail
        assert len(result.output.split('\n')) == 1 + 30 + 12 + 1
        assert result.exit_code == 0
        assert '/tasks' in result.output
        assert call(['flake8', '.']) == 0

    @pytest.fixture
    def csv_file(self, runner):
        cmd = ['create', '-n', 'tests/models.csv']
        result = runner.invoke(hobbit, cmd, obj={})
        assert result.exit_code == 0

    @pytest.mark.parametrize("gen_cmd", [
        ['--echo', 'gen', '-n', 'user', '-t', 'expirement'],
        ['--echo', 'gen', '-n', 'user', '-t', 'expirement', '-f', '--csv-path',
         os.path.join(BaseTest.root_path, 'tests', 'models.csv')],
    ])
    @chdir(wkdir)
    def test_new_expirement_tpl_and_gen_cmd(self, runner, gen_cmd, csv_file):
        assert os.getcwd() == self.wkdir

        # new project use expirement template
        cmd = [
            '--echo', 'new', '-n', 'haha', '-p', '1024',
            '-t', 'expirement']
        result = runner.invoke(hobbit, cmd, obj={})
        # start + files + mkdir + tail
        assert result.exit_code == 0
        assert len(result.output.split('\n')) == 1 + 31 + 11 + 1

        # gen new module
        result = runner.invoke(hobbit, gen_cmd, obj={})
        assert result.exit_code == 0
        assert len(result.output.split('\n')) == 5 + 1, result.output  # files

        # flake8 check
        assert call(['flake8', '.']) == 0
        # pytest
        assert call(['pytest']) == 0
