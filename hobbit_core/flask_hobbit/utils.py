# -*- encoding: utf-8 -*-
import os
import re
import six
from unicodedata import normalize


class dict2object(dict):
    """Dict to fake object that can use getattr.

    Examples::

        In [2]: obj = dict2object({'a': 2, 'c': 3})

        In [3]: obj.a
        Out[3]: 2

        In [4]: obj.c
        Out[4]: 3

    """

    def __getattr__(self, name):
        if name in self.keys():
            return self[name]
        raise AttributeError('object has no attribute {}'.format(name))

    def __setattr__(self, name, value):
        if not isinstance(name, six.string_types):
            raise TypeError('key must be string type.')
        self[name] = value


def secure_filename(filename):
    """Borrowed from werkzeug.utils.secure_filename.

    Pass it a filename and it will return a secure version of it. This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

        >>> secure_filename(u'哈哈.zip')
        '哈哈.zip'
        >>> secure_filename('My cool movie.mov')
        'My_cool_movie.mov'
        >>> secure_filename('../../../etc/passwd')
        'etc_passwd'
        >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
        'i_contain_cool_umlauts.txt'
    """
    if not isinstance(filename, six.text_type):
        try:
            filename = filename.decode('utf-8')
        except UnicodeDecodeError:
            raise Exception(
                'filename must be {}'.format(six.text_type))

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')

    filename = '_'.join(filename.split())

    if isinstance(filename, six.text_type):
        filename = normalize('NFKD', filename).encode('utf-8')
        if not six.PY2:
            filename = filename.decode('utf-8')

    if six.PY2 and not isinstance(filename, six.text_type):
        filename = filename.decode('utf-8', 'replace')

    filename_strip_re = re.compile(u'[^A-Za-z0-9\u4e00-\u9fa5_.-]')
    filename = filename_strip_re.sub('', filename).strip('._')

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    windows_device_files = (
        'CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
        'LPT2', 'LPT3', 'PRN', 'NUL',
    )
    if os.name == 'nt' and filename and \
            filename.split('.')[0].upper() in windows_device_files:
        filename = '_' + filename

    return filename
