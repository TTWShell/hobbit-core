# -*- encoding: utf-8 -*-
import pytest

from hobbit_core.flask_hobbit import db

from . import BaseTest


class TestEnumExt(BaseTest):

    def test_key_index(self):
        msg = u"EnumExt member must be tuple type and length equal 2."
        with pytest.raises(TypeError, match=msg):
            class ErrTypeEnum(db.EnumExt):
                CREATED = (0, u'新建', 'dda')

        msg = r"duplicate values found: .*, please check key or value."
        with pytest.raises(ValueError, match=msg):
            class ErrEnum(db.EnumExt):
                CREATED = (0, u'新建')
                FINISHED = (0, u'已完成')

    @pytest.fixture
    def TaskState(self):
        class _TaskState(db.EnumExt):
            CREATED = (0, u'新建')
            FINISHED = (1, u'已完成')
        return _TaskState

    def test_strict_dump(self, TaskState):
        assert 0 == TaskState.strict_dump('CREATED')
        assert u'新建' == TaskState.strict_dump('CREATED', True)

    def test_dump(self, TaskState):
        assert {'key': 0, 'value': u'新建'} == TaskState.dump('CREATED')

    def test_load(self, TaskState):
        assert 'FINISHED' == TaskState.load('FINISHED')
        assert 'FINISHED' == TaskState.load(1)
        assert 'CREATED' == TaskState.load(u'新建')
        assert TaskState.load(100) is None

    def test_to_opts(self, TaskState):
        opts = TaskState.to_opts()
        assert opts == [
            {'key': 0, 'value': u'新建'},
            {'key': 1, 'value': u'已完成'},
        ]
        opts = TaskState.to_opts(verbose=True)
        assert opts == [
            {'key': 0, 'label': 'CREATED', 'value': u'新建'},
            {'key': 1, 'label': 'FINISHED', 'value': u'已完成'},
        ]
