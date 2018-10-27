Hobbit-core's API Documentation
===============================

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
   :exclude-members: SurrogatePK, EnumExt

   .. autoclass:: SurrogatePK
       :members: __repr__

   .. autoclass:: EnumExt
       :members:

       .. automethod:: strict_dump
       .. automethod:: dump
       .. automethod:: load
       .. automethod:: to_opts

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
   :exclude-members: ORMSchema, SchemaMixin, PagedSchema

   .. autoclass:: ORMSchema
       :members:
       :exclude-members: make_instance

   .. autoclass:: SchemaMixin
       :members:

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



