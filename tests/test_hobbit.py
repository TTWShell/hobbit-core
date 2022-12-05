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
        'name,template,dist',
        itertools.product(
            ['haha'], templates,
            [None, '.', wkdir]))
    @chdir(wkdir)
    def test_new_cmd(self, runner, name, template, dist):
        options = [
            '--echo', 'new', '-p 1024', '-n', name,  '-t', template]
        if dist:
            assert os.getcwd() == os.path.abspath(dist)
            options.extend(['-d', dist])

        result = runner.invoke(hobbit, options, obj={})
        assert result.exit_code == 0, result.output
        assert 'mkdir\t{}'.format(self.wkdir) in result.output
        assert 'render\t{}'.format(self.wkdir) in result.output

        file_nums = {
            # tart + 29 files + 11 dir + 1 end + empty
            'shire':  1 + 27 + 11 + 1 + 1 - 1,
            'rivendell':  1 + 29 + 11 + 1,
        }
        assert len(result.output.split('\n')) == file_nums[f'{template}']

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

    @chdir(wkdir)
    def test_dev_init_cmd(self, runner):
        # new project use rivendell template
        cmd = ['--echo', 'new', '-n', 'haha', '-p', '1024', '-t', 'rivendell']
        result = runner.invoke(hobbit, cmd, obj={})
        assert result.exit_code == 0

        result = runner.invoke(hobbit, ['dev', 'init', '--all'], obj={})
        assert result.exit_code == 0, result.output
