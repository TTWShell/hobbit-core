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

    hobbit --echo startproject -n demo -d .

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

flask_hobbit.db
^^^^^^^^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.db
   :members:
   :undoc-members:
   :exclude-members: SurrogatePK

   .. autoclass:: SurrogatePK
       :members: __repr__

flask_hobbit.pagination
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.pagination
   :members:
   :undoc-members:

flask_hobbit.schemas
^^^^^^^^^^^^^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.schemas
   :members:
   :undoc-members:
   :exclude-members: PagedSchema

   .. autoclass:: PagedSchema
       :members:

flask_hobbit.response
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.response
   :members:
   :undoc-members:

flask_hobbit.utils
^^^^^^^^^^^^^^^^^^

.. automodule:: hobbit_core.flask_hobbit.utils
   :members:
   :undoc-members:


Indices and tables
==================

* :ref:`search`


Others
======

.. toctree::
    :maxdepth: 2

    changelog
