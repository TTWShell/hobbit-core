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
# The amount files of `shire[new]` + `rivendell[new]`
assert len(package_data) == 27 + 28, \
    'nums of tepl files error, {}'.format(len(package_data))
package_data.append('py.typed')


long_description_content_type = 'text/markdown'
try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
    long_description_content_type = 'text/x-rst'
except (OSError, ImportError):
    long_description = open('README.md').read()


setup(
    name='hobbit-core',
    version='3.0.0',
    python_requires='>=3.7, <4',
    description='Hobbit - A flask project generator.',
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    author='Legolas Bloom',
    author_email='zhanhsw@gmail.com',
    url='https://github.com/TTWShell/hobbit-core',
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(),
    package_data={'hobbit': package_data},
    install_requires=[],
    extras_require={
        'hobbit_core': [
            'Flask>=2.0,<3',
            'flask-marshmallow>=0.14.0,<1',
            'Flask-Migrate>=4,<5',
            'flask-shell-ipython>=0.4.1',
            'SQLAlchemy>=1.4.0,< 2',
            'Flask-SQLAlchemy>=3.0.0,<4',
            'marshmallow-enum>=1.5.1,<2',
            'marshmallow-sqlalchemy>=0.26.1,<3',
            'webargs>=8.0.0,<9',
            'mypy-extensions>=0.4.3',
            'pyyaml>=5.4.1,<6',
            'marshmallow>=3.0.0,<4',
        ],
        'hobbit': [
            'Click>=6.7',
            'Jinja2>=3.0',
            'inflect>=2.1.0',
            'markupsafe>=2.0.1',
        ],
    },
    entry_points={
        'console_scripts': 'hobbit = hobbit:main [hobbit]'
    },
)
