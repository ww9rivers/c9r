#!/usr/bin/env python3

"""
| This file is part of the c9r package
| Copyrighted by Wei Wang <ww@9rivers.com>
| License: https://github.com/ww9rivers/c9r/wiki/License

This is copied from web2py/gluon/storage.py, to replace Thingy eventually.

Contains classes:

- Storage
"""

import json


class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`, and setting obj.foo = None deletes item foo.

    Example::

        >>> o = Storage(a=1)
        >>> print(o.a)
        1

        >>> o['a']
        1

        >>> o.a = 2
        >>> print(o['a'])
        2

        >>> del o.a
        >>> print(o.a)
        None
    """
    __slots__ = ()
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getitem__ = dict.get
    __getattr__ = dict.get
    __repr__ = lambda self: '<Storage %s>' % dict.__repr__(self)
    # http://stackoverflow.com/questions/5247250/why-does-pickle-getstate-accept-as-a-return-value-the-very-instance-it-requi
    __getstate__ = lambda self: None
    __copy__ = lambda self: Storage(self)

    def getlist(self, key):
        """
        Returns a Storage value as a list.

        If the value is a list it will be returned as-is.
        If object is None, an empty list will be returned.
        Otherwise, `[value]` will be returned.

        Example output for a query string of `?x=abc&y=abc&y=def`::

            >>> request = Storage()
            >>> request.vars = Storage()
            >>> request.vars.x = 'abc'
            >>> request.vars.y = ['abc', 'def']
            >>> request.vars.getlist('x')
            ['abc']
            >>> request.vars.getlist('y')
            ['abc', 'def']
            >>> request.vars.getlist('z')
            []

        """
        value = self.get(key, [])
        if value is None or isinstance(value, (list, tuple)):
            return value
        else:
            return [value]

    def getfirst(self, key, default=None):
        """
        Returns the first value of a list or the value itself when given a
        `request.vars` style key.

        If the value is a list, its first item will be returned;
        otherwise, the value will be returned as-is.

        Example output for a query string of `?x=abc&y=abc&y=def`::

            >>> request = Storage()
            >>> request.vars = Storage()
            >>> request.vars.x = 'abc'
            >>> request.vars.y = ['abc', 'def']
            >>> request.vars.getfirst('x')
            'abc'
            >>> request.vars.getfirst('y')
            'abc'
            >>> request.vars.getfirst('z')

        """
        values = self.getlist(key)
        return values[0] if values else default

    def getlast(self, key, default=None):
        """
        Returns the last value of a list or value itself when given a
        `request.vars` style key.

        If the value is a list, the last item will be returned;
        otherwise, the value will be returned as-is.

        Simulated output with a query string of `?x=abc&y=abc&y=def`::

            >>> request = Storage()
            >>> request.vars = Storage()
            >>> request.vars.x = 'abc'
            >>> request.vars.y = ['abc', 'def']
            >>> request.vars.getlast('x')
            'abc'
            >>> request.vars.getlast('y')
            'def'
            >>> request.vars.getlast('z')

        """
        values = self.getlist(key)
        return values[-1] if values else default

def load_storage(read_fro):
    '''Read JSON data from a /read_fro/ object to create a Storage object.

    /read_fro/  A file-like object to read from. It is assumed to be a filename
                if it is a string.
    '''
    fp = None
    try:
        fp = open(read_fro, 'r') if isinstance(read_fro, str) else read_fro
        storage = json.load(fp)
    finally:
        if fp and fp != read_fro:
            fp.close()
    return Storage(storage)


def save_storage(storage, save_to, indent=None):
    '''Save a given /storage/ object to specified object to /save_to/.

    /storage/  A Storage object to save.
    /save_to/  A file-like object to save to. It is assumed to be a filename
               if it is a string.
    '''
    fp = None
    try:
        fp = open(save_to, 'w') if isinstance(save_to, str) else save_to
        json.dump(storage, fp, indent=indent)
    finally:
        if fp and fp != save_to:
            fp.close()

if __name__ == '__main__':
    import doctest
    doctest.testfile('test/jso.test')
