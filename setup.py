import os
from setuptools import setup, find_packages

import hobbit_core


def gen_data(data_root='hobbit/static/bootstrap'):
    data = [os.path.join(data_root, '*.jinjia2')]
    for fn in os.listdir(os.path.join('hobbit_core', data_root)):
        if os.path.isdir(os.path.join('hobbit_core', data_root, fn)):
            data.extend(gen_data(os.path.join(data_root, fn)))
    return data


setup(
    name='hobbit_core',
    version='.'.join(str(i) for i in hobbit_core.VERSION),
    description='Hobbit - Change the World.',
    author='Legolas Bloom',
    author_email='zhanhsw@gmail.com',
    packages=find_packages(),
    package_data={"": ['LICENSE'], 'hobbit_core': gen_data()},
    install_requires=[
        'Click==6.7',
        'Jinja2==2.9.6',
    ],
    entry_points={
        'console_scripts': 'hobbit = hobbit_core.hobbit:main'
    },
)
