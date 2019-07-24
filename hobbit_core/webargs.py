from webargs.flaskparser import FlaskParser


class CustomParser(FlaskParser):

    def parse_arg(self, name, field, req, locations=None):
        ret = super().parse_arg(name, field, req, locations=locations)
        if hasattr(ret, 'strip'):
            return ret.strip()
        return ret


parser = CustomParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
