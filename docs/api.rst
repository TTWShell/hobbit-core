Hobbit-core's API Documentation
===============================

hobbit cmd
------------------

hobbit - A flask project generator.

.. autofunction:: hobbit.bootstrap.new

hobbit_core
------------------------

A flask extension that take care of base utils.

.. automodule:: hobbit_core
   :members:
   :undoc-members:

db
^^

.. automodule:: hobbit_core.db
   :members:
   :undoc-members:
   :exclude-members: SurrogatePK, EnumExt, EnumExtMeta

   .. autoclass:: BaseModel
       :members: __repr__

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

.. automodule:: hobbit_core.pagination
   :members:
   :undoc-members:

schemas
^^^^^^^

.. automodule:: hobbit_core.schemas
   :members:
   :undoc-members:
   :exclude-members: ORMSchema, SchemaMixin, PagedSchema, EnumSetMeta

   .. autoclass:: ORMSchema
       :members:
       :exclude-members: make_instance

   .. autoclass:: SchemaMixin
       :members:

   .. autoclass:: PagedSchema
       :members:

utils
^^^^^

.. automodule:: hobbit_core.utils
   :members:
   :undoc-members:


response
^^^^^^^^

.. automodule:: hobbit_core.response
   :members:
   :undoc-members:

err_handler
^^^^^^^^^^^

.. automodule:: hobbit_core.err_handler
   :members:



