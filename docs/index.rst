Welcome to hobbit-core's documentation!
=======================================

`changelog <changelog.html>`_ //
`github <https://github.com/TTWShell/hobbit-core>`_ //
`pypi <https://pypi.org/project/hobbit-core/>`_ //
`issues <https://github.com/TTWShell/hobbit-core/issues>`_

**Why do we need this project?** Answer is `Convention over configuration. <https://en.wikipedia.org/wiki/Convention_over_configuration>`_


Tutorial
========

Get it right now::

    pip install hobbit-core

Create your flask project::

    hobbit --echo startproject -n demo -d . --example

Run flask app::

    FLASK_APP=demo/run.py flask run

It works::

     * Serving Flask app "demo/run.py"
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

If not skip example(Please see --example/--no-example options), you can get project tree like this::

    .
    ├── app
    │   ├── __init__.py
    │   ├── configs
    │   │   ├── __init__.py
    │   │   ├── default.py
    │   │   ├── development.py
    │   │   ├── production.py
    │   │   └── testing.py
    │   ├── core
    │   │   └── __init__.py
    │   ├── exts.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   └── example.py
    │   ├── run.py
    │   ├── schemas
    │   │   ├── __init__.py
    │   │   └── example.py
    │   ├── utils
    │   │   └── __init__.py
    │   └── views
    │       ├── __init__.py
    │       └── example.py
    ├── docs
    ├── requirements.txt
    └── tests
        ├── __init__.py
        ├── conftest.py
        └── test_example.py

app
---

App dir saved all business layer codes. You must ensure dir name is app based on *convention over configuration*.

configs
^^^^^^^

In a hobbit app, we auto load config by FLASK_ENV. If FLASK_ENV=production, used ``configs/production.py`` file.

exts
^^^^

`Why use exts.py to instance extension? <https://stackoverflow.com/questions/42909816/can-i-avoid-circular-imports-in-flask-and-sqlalchemy/51739367#51739367>`_


API
===

hobbit_core.hobbit
------------------

hobbit - A flask project generator.

.. autofunction:: hobbit_core.hobbit.bootstrap.startproject

hobbit_core.flask_hobbit
------------------------

A flask extension that take care of base utils.

.. automodule:: hobbit_core.flask_hobbit
   :members:
   :undoc-members:

db
^^

.. automodule:: hobbit_core.flask_hobbit.db
   :members:
   :undoc-members:
   :exclude-members: SurrogatePK

   .. autoclass:: SurrogatePK
       :members: __repr__

pagination
^^^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.pagination
   :members:
   :undoc-members:

schemas
^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.schemas
   :members:
   :undoc-members:
   :exclude-members: PagedSchema

   .. autoclass:: PagedSchema
       :members:

utils
^^^^^

.. automodule:: hobbit_core.flask_hobbit.utils
   :members:
   :undoc-members:


response
^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.response
   :members:
   :undoc-members:

err_handler
^^^^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.err_handler
   :members:


Indices and tables
==================

* :ref:`search`


Others
======

.. toctree::
    :maxdepth: 2

    changelog
