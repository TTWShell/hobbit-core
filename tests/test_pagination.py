import pytest

import webargs
from hobbit_core.flask_hobbit.pagination import PageParams

from . import BaseTest


class TestPagination(BaseTest):

    def test_page_params(self, web_request, parser):
        # test default
        @parser.use_kwargs(PageParams, web_request, locations=('query', ))
        def viewfunc(page, page_size, order_by):
            return {'page': page, 'page_size': page_size, 'order_by': order_by}

        assert viewfunc() == {'order_by': ['-id'], 'page': 1, 'page_size': 10}

        # test page_size_range
        web_request.query = {'page_size': 101}
        msg = "webargs.core.ValidationError: {'page_size': " + \
            "['Must be between 10 and 100.']}"
        with pytest.raises(webargs.core.ValidationError, message=msg):
            viewfunc()

        # test order_by
        web_request.query = {'order_by': 'id,-11'}
        msg = "webargs.core.ValidationError: {'order_by': " + \
            "{1: ['String does not match expected pattern.']}}"
        with pytest.raises(webargs.core.ValidationError, message=msg):
            viewfunc()

        web_request.query = {'order_by': 'id,-aaa'}
        assert viewfunc() == {
            'order_by': ['id', '-aaa'], 'page': 1, 'page_size': 10}

        web_request.query = {'order_by': ''}
        assert viewfunc() == {
            'order_by': [''], 'page': 1, 'page_size': 10}
