# -*- encoding: utf-8 -*-
from hobbit_core.flask_hobbit.utils import secure_filename

from . import BaseTest, python3_only


class TestUtils(BaseTest):

    @python3_only
    def test_secure_filename(self):
        filenames = (
            '哈哈.zip', '../../../etc/passwd', 'My cool movie.mov',
            '__filename__', 'foo$&^*)bar',
            'i contain cool \xfcml\xe4uts.txt',
        )
        excepted = (
            '哈哈.zip', 'etc_passwd', 'My_cool_movie.mov',
            'filename', 'foobar',
            'i_contain_cool_umlauts.txt',
        )
        for i, filename in enumerate(filenames):
            assert secure_filename(filename) == excepted[i]
