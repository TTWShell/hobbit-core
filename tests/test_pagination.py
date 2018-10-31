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

        @parser.use_kwargs(PageParams, web_request, locations=('query', ))
        def viewfunc(page, page_size, order_by):
            return {'page': page, 'page_size': page_size, 'order_by': order_by}

        msg = "webargs.core.ValidationError: {'page_size': " + \
            "['Must be between 10 and 100.']}"
        with pytest.raises(webargs.core.ValidationError, message=msg):
            viewfunc()
