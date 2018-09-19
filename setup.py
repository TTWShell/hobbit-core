import os
from setuptools import setup, find_packages

import hobbit_core

ROOT_PATH = os.path.split(os.path.abspath(os.path.join(__file__)))[0]
src_path = os.path.join(ROOT_PATH, 'hobbit_core')


def gen_data(data_root='hobbit/static/bootstrap'):
    """just for collect static files.
    """
    data = [os.path.join(data_root, '*.jinja2')]
    for fn in os.listdir(os.path.join(src_path, data_root)):
        if os.path.isdir(os.path.join(src_path, data_root, fn)):
            data.extend(gen_data(os.path.join(data_root, fn)))
    return data


try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(OSError, ImportError):
    long_description = open('README.md').read()


setup(
    name='hobbit-core',
    version='.'.join(str(i) for i in hobbit_core.VERSION),
    python_requires='>=3.6',
    description='Hobbit - A flask project generator.',
    long_description=long_description,
    author='Legolas Bloom',
    author_email='zhanhsw@gmail.com',
    url='https://github.com/TTWShell/hobbit-core',
    packages=find_packages(),
    package_data={'': ['LICENSE'], 'hobbit_core': gen_data()},
    install_requires=[
        'Click==6.7',
        'Jinja2==2.10',

        'Flask==1.0.2',
        'flask-marshmallow==0.9.0',
        'Flask-Migrate==2.2.1',
        'flask-shell-ipython==0.3.1',
        'Flask-SQLAlchemy==2.3.2',
        'marshmallow-enum==1.4.1',
        'marshmallow-sqlalchemy==0.14.1',
        'webargs==4.0.0',
    ],
    entry_points={
        'console_scripts': 'hobbit = hobbit_core.hobbit:main'
    },
)
