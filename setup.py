from setuptools import setup, find_packages

import hobbit_core

data = [
]

setup(
    name='hobbit_core',
    version='.'.join(str(i) for i in hobbit_core.VERSION),
    description='Hobbit - Change the World.',
    author='Legolas Bloom',
    author_email='zhanhsw@gmail.com',
    packages=find_packages(),
    package_data={"": ['LICENSE'], 'hobbit_core': data},
    install_requires=[
        'Click==6.7',
        'Jinja2==2.9.6',
    ],
    entry_points={
        'console_scripts': 'hobbit = hobbit_core.hobbit:main'
    },
)
