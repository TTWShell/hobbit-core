from collections.abc import Mapping

from webargs.flaskparser import FlaskParser


def strip_whitespace(value):
    if isinstance(value, str):
        value = value.strip()
    # you'll be getting a MultiDictProxy here potentially, but it should work
    elif isinstance(value, Mapping):
        return {k: strip_whitespace(value[k]) for k in value}
    elif isinstance(value, (list, set)):
        return type(value)(map(strip_whitespace, value))
    return value


class CustomParser(FlaskParser):

    def _load_location_data(self, **kwargs):
        data = super()._load_location_data(**kwargs)
        return strip_whitespace(data)


parser = CustomParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
