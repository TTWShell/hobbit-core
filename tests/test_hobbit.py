
from click.testing import CliRunner

from hobbit_core.hobbit import main

from . import BaseTest, rmdir


class TestHobbit(BaseTest):
    wkdir = '/tmp/hobbit-tox-test'

    def setup_method(self, method):
        rmdir(self.wkdir)
        super().setup_method(method)

    def test_startproject(self):
        runner = CliRunner()
        result = runner.invoke(main)
        assert result.exit_code == 0
