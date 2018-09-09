import os
from setuptools import setup, find_packages

import hobbit_core


def gen_data(data_root='hobbit/static/bootstrap'):
    data = [os.path.join(data_root, '*.jinja2')]
    for fn in os.listdir(os.path.join('hobbit_core', data_root)):
        if os.path.isdir(os.path.join('hobbit_core', data_root, fn)):
            data.extend(gen_data(os.path.join(data_root, fn)))
    return data


data = [
    'hobbit/static/bootstrap/*.jinja2',
    'hobbit/static/bootstrap/shire/*.jinja2',
    'hobbit/static/bootstrap/shire/{{ project_name }}/*.jinja2',
    'hobbit/static/bootstrap/shire/tests/*.jinja2',
    'hobbit/static/bootstrap/shire/docs/*.jinja2',
    'hobbit/static/bootstrap/shire/configs/*.jinja2',
    'hobbit/static/bootstrap/shire/configs/conf.d/*.jinja2',
]


setup(
    name='hobbit_core',
    version='.'.join(str(i) for i in hobbit_core.VERSION),
    description='Hobbit - Change the World.',
    author='Legolas Bloom',
    author_email='zhanhsw@gmail.com',
    packages=find_packages(),
    package_data={'': ['LICENSE'], 'hobbit_core': data},
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
