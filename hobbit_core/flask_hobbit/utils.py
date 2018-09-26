import six


class dict2object(dict):
    """Dict to fake object that can use getattr.

    Examples::

        In [2]: obj = dict2object({'a':2, 'c':3})

        In [3]: obj.a
        Out[3]: 2

        In [4]: obj.c
        Out[4]: 3

    """

    def __getattr__(self, name):
        if name in self.keys():
            return self[name]
        raise AttributeError('object has no attribute {}'.format(name))

    def __setattr__(self, name, value):
        if not isinstance(name, six.string_types):
            raise TypeError('key must be string type.')
        self[name] = value
