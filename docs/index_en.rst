Hobbit-core's documentation
===========================

`changelog <changelog.html>`_ //
`github <https://github.com/TTWShell/hobbit-core>`_ //
`pypi <https://pypi.org/project/hobbit-core/>`_ //
`issues <https://github.com/TTWShell/hobbit-core/issues>`_ //
`API doc <api.html>`_ //
`中文文档 <index.html>`_

A flask project generator. Based on Flask + SQLAlchemy + marshmallow + webargs.

A hobbit app contains RESTful API, celery, unit test, gitlab-ci/cd、docker compose etc.

**Why do we need this project?** Answer is `Convention over configuration. <https://en.wikipedia.org/wiki/Convention_over_configuration>`_


Tutorial
========

Get it right now::

    pip install hobbit-core

Create your flask project::

    hobbit --echo new -n demo -d . -p 5000 --celery

Run flask app::

    FLASK_APP=app/run.py flask run

It works::

     * Serving Flask app "app/run.py"
     * Environment: production
       WARNING: Do not use the development server in a production environment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

You can request ``http://127.0.0.1:5000/api/ping/``

Other tips::

    hobbit --help


Project Tree
============

::

    .
    ├── Dockerfile
    ├── app
    │   ├── __init__.py
    │   ├── configs
    │   │   ├── __init__.py
    │   │   ├── default.py
    │   │   ├── development.py
    │   │   ├── production.py
    │   │   └── testing.py
    │   ├── core
    │   │   └── __init__.py
    │   ├── exts.py
    │   ├── models
    │   │   └── __init__.py
    │   ├── run.py
    │   ├── schemas
    │   │   └── __init__.py
    │   ├── tasks
    │   │   └── __init__.py
    │   ├── utils
    │   │   └── __init__.py
    │   └── views
    │       ├── __init__.py
    │       └── ping.py
    ├── configs
    │   └── gunicorn-logging.ini
    ├── deploy.sh
    ├── docker-compose.yml
    ├── docs
    │   └── index.apib
    ├── pytest.ini
    ├── requirements.txt
    └── tests
        ├── __init__.py
        ├── conftest.py
        └── test_ping.py

Dockerfile
----------

Build image for run web server. For more information about dockerfile, please visit : `Dockerfile reference <https://docs.docker.com/engine/reference/builder/#usage>`_.

app
---

App dir saved all business layer codes. You must ensure dir name is app based on *convention over configuration*.

configs
^^^^^^^

In a hobbit app, we auto load config by FLASK_ENV. If FLASK_ENV=production, used ``configs/production.py`` file.

core
^^^^

All complicated function, base class etc.

exts.py
^^^^^^^

To avoid circular imports in Flask and flask extention, exts.py used. `Why use exts.py to instance extension? <https://stackoverflow.com/questions/42909816/can-i-avoid-circular-imports-in-flask-and-sqlalchemy/51739367#51739367>`_

models
^^^^^^

Create your models here.

run.py
^^^^^^

schemas
^^^^^^^

Create your marshmallow scheams here.

tasks
^^^^^

Celery tasks here.

utils
^^^^^

All common utils here.

views
^^^^^

Create your views here.

deploy.sh
---------

A script for deploy.

docker-compose.yml
^^^^^^^^^^^^^^^^^^

Base docker compose file. Run app::

    docker-compose up

docs
----

API doc etc.

logs
----

All logs for app, nginx etc.

tests
-----

Create your tests here. Recommended use `pytest <https://docs.pytest.org/en/latest/>`_.


Others
======

.. toctree::
    :maxdepth: 2

    changelog
    api
