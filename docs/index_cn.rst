Hobbit-core中文文档
===================

`changelog <changelog.html>`_ //
`github <https://github.com/TTWShell/hobbit-core>`_ //
`pypi <https://pypi.org/project/hobbit-core/>`_ //
`issues <https://github.com/TTWShell/hobbit-core/issues>`_ //
`API文档 <api.html>`_ //
`EN version <index.html>`_

基于 Flask + SQLAlchemy + marshmallow + webargs 的 flask 项目生成器。

包含 RESTful API、单元测试、gitlab-ci/cd、docker compose 一套解决方案。后续考虑更好的自动文档工具（目前有 apispec ）。

**为什么我开发了这个项目？** 可以参考这一设计范式： `Convention over configuration. <https://en.wikipedia.org/wiki/Convention_over_configuration>`_


简易教程
========

快速安装::

    pip install hobbit-core

使用 ``hobbit`` 命令自动生成你的flask项目::

    hobbit --echo startproject -n demo -d . --example -p 5000

参数 ``--example`` 会同时生成一个完整的api及其测试范例，使用以下项目启动server::

    FLASK_APP=app/run.py flask run

你可以在控制台看到类似如下信息::

     * Serving Flask app "app/run.py"
     * Environment: production
       WARNING: Do not use the development server in a production environment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

访问 ``http://127.0.0.1:5000/api/ping/``

有关 ``hobbit`` 的使用，直接查看帮助文档::

    hobbit --help


项目结构
========

如果使用 ``--example`` 参数（查看 ``--example/--no-example`` 相关帮助信息），你将会得到如下所示的项目结构::

    .
    ├── Dockerfile
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
    ├── deploy.sh
    ├── docker-compose.yml
    ├── docs
    ├── logs
    ├── requirements.txt
    └── tests
        ├── __init__.py
        ├── conftest.py
        └── test_example.py

Dockerfile
----------

使用docker来运行我们的web服务，基于同一个docker image运行测试，由此保证开发环境、测试环境、运行时环境一致。你可以在 `Dockerfile reference <https://docs.docker.com/engine/reference/builder/#usage>`_ 查看有关Dockerfile的语法。

app
---

app文件夹保存了所有业务层代码。基于 **约定优于配置** 范式，这个文件夹名字及所有其他文件夹名字 **禁止修改** 。

configs
^^^^^^^

基于flask设计，我们使用环境变量 ``FLASK_ENV`` 加载不同环境的配置文件。例如 ``FLASK_ENV=production`` ，会自动加载 ``configs/production.py`` 这个文件作为配置文件。

core
^^^^

core文件夹约定编写自定义的基础类库代码，复杂的业务层代码。

exts.py
^^^^^^^

flask项目很容易产生循环引用问题， ``exts.py`` 文件的目的就是避免产生这个问题。你可以看下这个解释： `Why use exts.py to instance extension? <https://stackoverflow.com/questions/42909816/can-i-avoid-circular-imports-in-flask-and-sqlalchemy/51739367#51739367>`_

models
^^^^^^

所有数据库模型定义在这里。

run.py
^^^^^^

web项目的入口。你将在这里注册路由、注册命令等等操作。

schemas
^^^^^^^

定义所有的 marshmallow scheams。我们使用marshmallow来序列化api输出，类似 ``django-rest-framework`` 的效果。

utils
^^^^^

定义所有的公用工具函数。

views
^^^^^

路由及简单业务逻辑。

deploy.sh
---------

一个简易的部署脚本。配合ci/cd系统一起工作。

docker-compose.yml
^^^^^^^^^^^^^^^^^^

基本的 docker compose 配置文件。考虑到单机部署需求，自动生成了一个简易的配置，启动项目::

    docker-compose up

docs
----

API 文档、model 设计文档、架构设计文档、需求文档等等项目相关的文档。

logs
----

运行时的log文件。

tests
-----

所有的测试case. 推荐使用 `pytest <https://docs.pytest.org/en/latest/>`_ 测试。


Others
======

.. toctree::
    :maxdepth: 2

    changelog
    api
