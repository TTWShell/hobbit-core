Change history
==============

1.4.0 (2019-05-06)
******************

* Add template for 4-layers (view、schema、service、model).
* Split hobbit cmd and hobbit_core lib, now install cmd should be `pip install "hobbit-core[hobbit,hobbit_core]"`.
* Remove flask_hobbit when import (`hobbit_core.flask_hobbit.db import transaction` --> `from hobbit_core.db import transaction`).

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
