import os

from click.testing import CliRunner

from hobbit_core.hobbit import main as hobbit

from . import BaseTest, rmdir, chdir


class TestHobbit(BaseTest):
    wkdir = os.path.abspath('hobbit-tox-test')

    def setup_method(self, method):
        rmdir(self.wkdir)
        super().setup_method(method)

    def teardown_method(self, method):
        rmdir(self.wkdir)
        super().teardown_method(method)

    def test_hobbit_cmd(self):
        runner = CliRunner()

        result = runner.invoke(hobbit)
        assert result.exit_code == 0

        result = runner.invoke(hobbit, ['doesnotexistcmd'], obj={})
        assert 'Error: cmd not exist: doesnotexistcmd' in result.output

    @chdir(wkdir)
    def test_startproject_cmd_nodist(self):
        assert os.getcwd() == self.wkdir
        runner = CliRunner()

        result = runner.invoke(hobbit, ['--echo', 'startproject'], obj={})
        assert result.exit_code == 2
        assert 'Error: Missing option "-n" / "--name".' in result.output

        result = runner.invoke(
            hobbit, ['--echo', 'startproject', '-n', 'haha', '-f'], obj={})
        assert result.exit_code == 0
        assert 'mkdir\t{}'.format(self.wkdir) in result.output
        assert 'render\t{}'.format(self.wkdir) in result.output

    def test_startproject_cmd_dist(self):
        runner = CliRunner()

        result = runner.invoke(
            hobbit,
            ['--echo', 'startproject', '-n', 'haha', '-f', '-d', self.wkdir],
            obj={})
        assert result.exit_code == 0
        assert 'mkdir\t{}'.format(self.wkdir) in result.output
        assert 'render\t{}'.format(self.wkdir) in result.output
