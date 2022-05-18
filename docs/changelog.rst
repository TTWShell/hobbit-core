Change history
==============

2.2.3 (2022-05-18)
******************

* Support use nested=None(`@transaction(db.session, nested=None)`) to avoid bug from `flask_sqlalchemy.models_committed` signal.

2.2.2 (2022-02-17)
******************

* Refactor tpl: Auto nested blueprint.
* Refactor tpl: ping and options api were merged into tools.
* Enhance teardown_method in test: auto handle deps when delete table.
* Fix some typo.

2.2.1 (2021-12-01)
******************

* Add `err_handler.HobbitException`: Base class for all hobbitcore-related errors.

2.2.0 (2021-11-18)
******************

* Support Python 3.10.

2.1.1 (2021-10-25)
******************

* Add util `bulk_create_or_update_on_duplicate`, support MySQL and postgreSQL.

2.1.0 (2021-10-25, unused)

* This filename has already been used (Wrong file pushed to pypi.org).

2.0.4 (2021-07-13)
******************

* Support set `HOBBIT_RESPONSE_MESSAGE_MAPS` to use self-defined response message.

2.0.3 (2021-07-08)
******************

* Fix set response.xxxResult code = 0.

2.0.2 (2021-07-08)
******************

* Fix response message err when code is 200 or 400.
* Support set `HOBBIT_USE_CODE_ORIGIN_TYPE = True` to return origin type of code in response.

2.0.1 (2021-06-21)
******************

* Add data field for response.Result: return Real response payload.
* Bugfix: tests.BaseTest.teardown_method miss `app.app_context()`.

2.0.0 (2021-06-20)
******************

* Upgrade webargs to version 8.x.x.
* Lock SQLAlchemy version less than 1.4.0 (session.autobegin feature doesn't look like a good idea).
* Lock Flask version less than 2.x.x (because some bugs).
* Upgrade and lock marshmallow>=3.0.0,<4.
* Remove hobbit gen cmd.

1.4.4 (2020-03-25)
******************

* Fix webargs 6.x.x: limit version < 6.

1.4.3 (2019-07-24)
******************

* Add CustomParser for automatically trim leading/trailing whitespace from argument values(`from hobbit_core.webargs import use_args, use_kwargs`).
* Add `HOBBIT_UPPER_SEQUENCE_NAME` config for upper db's sequence name.
* Fixs some err in template.

1.4.2 (2019-06-13)
******************

* Add `db.BaseModel` for support Oracle id sequence.

1.4.1 (2019-05-23)
******************

* Add template for 4-layers (view、schema、service、model).
* Add options api for query all consts defined in `app/models/consts`.
* Add `create` command to generate a csv file that defines some models to use in the `gen` command.
* Removed example code.
* Split hobbit cmd and hobbit_core lib, now install cmd should be `pip install "hobbit-core[hobbit,hobbit_core]"`.
* Remove flask_hobbit when import (`hobbit_core.flask_hobbit.db import transaction` --> `from hobbit_core.db import transaction`).
* Enhance gen cmd: now can auto create CRUD API and tests.
* Fix typo.
* Update some test cases.

1.4.0 (Obsolete version)
************************

1.3.1 (2019-02-26)
******************

* The strict parameter is removed in marshmallow >= 3.0.0.

1.3.0 (2019-01-14)
******************

* Add import_subs util for auto import models、schemas、views in module/__init__.py file.
* Add index for created_at、updated_at cloumn and default order_by id.
* Add validate for PageParams.
* Add hobbit gen cmd for auto render views.py, models.py, schemas.py etc when start a feature dev.
* Add ErrHandler.handler_assertion_error.
* Add db.transaction decorator, worked either autocommit True or False.
* pagination return dict instead of class, order_by can set None for
* traceback.print_exc() --> logging.error.
* Foreign key fields support ondelete, onupdate.
* Hobbit startproject cmd support celery option.

1.2.5 (2018-10-30)
******************

* Add ModelSchema(Auto generate load and dump func for EnumField).
* Add logging config file.
* Add EnumExt implementation.
* Fix use_kwargs with fileds.missing=None and enhanced.

1.2.4 (2018-10-18)
******************

* Fix SuccessResult status arg not used.

1.2.3 (2018-10-18)
******************

* Add utils.use_kwargs, fix webargs's bug.

1.2.2 (2018-10-16)
******************

* Add SchemaMixin & ORMSchema use in combination with db.SurrogatePK.
* Now print traceback info when server 500.
* Fix miss hidden files when sdist.

1.2.1 (2018-10-12)
******************

* secure_filename support py2 & py3.

1.2.0 (2018-10-11)
******************

* Gitlab CI/CD support.
* Add secure_filename util.
* Enhance deploy, can deploy to multiple servers.
* Add --port option for startproject cmd.

1.1.0 (2018-09-29)
******************

* Beta release.
* Fix hobbit create in curdir(.) err.
* Add dict2object util.
* Project tree confirmed.
* Add tutorial、project tree doc.
* Add example options for startproject cmd.


1.0.0 (2018-09-25)
******************

* Alpha release.
* flask_hobbit release.

0.0.[1-9]
*********

* hobbit cmd released.
* Incompatible production version.
