import os
from pathlib import Path, PurePath
from setuptools import setup, find_packages

SUFFIX = '.jinja2'
ROOT_PATH = os.path.split(os.path.abspath(os.path.join(__file__)))[0]
src_path = os.path.join(ROOT_PATH, 'hobbit')


def gen_data(data_root='static'):
    """just for collect static files.
    """
    return [fpath.as_posix() for fpath in Path(
        PurePath(src_path) / data_root).glob(f'**/*{SUFFIX}')]


package_data = gen_data()
# The amount files of `shire[new,gen]` + `rivendell[...]`
assert len(package_data) == 30 + 4 + 31 + 5, \
    'nums of tepl files error, {}'.format(len(package_data))
package_data.append('py.typed')


try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(OSError, ImportError):
    long_description = open('README.md').read()


setup(
    name='hobbit-core',
    version='1.4.4',
    python_requires='>=3.6, <4',
    description='Hobbit - A flask project generator.',
    long_description=long_description,
    author='Legolas Bloom',
    author_email='zhanhsw@gmail.com',
    url='https://github.com/TTWShell/hobbit-core',
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(),
    package_data={'hobbit': package_data},
    install_requires=[],
    extras_require={
        'hobbit_core': [
            'Flask>=1.0.2',
            'flask-marshmallow>=0.9.0',
            'Flask-Migrate>=2.2.1',
            'flask-shell-ipython>=0.3.1',
            'Flask-SQLAlchemy>=2.3.2',
            'marshmallow-enum>=1.4.1',
            'marshmallow-sqlalchemy>=0.14.1',
            'webargs>=5.1.3, <6',
            'mypy-extensions==0.4.1',
            'pyyaml>=4.2b1',
            'marshmallow==v3.0.0rc6',
        ],
        'hobbit': [
            'Click>=6.7',
            'Jinja2>=2.10',
            'inflect>=2.1.0',
        ],
    },
    entry_points={
        'console_scripts': 'hobbit = hobbit:main [hobbit]'
    },
)
