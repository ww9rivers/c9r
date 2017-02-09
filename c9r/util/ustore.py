#!/usr/bin/env python
##
## $Id: jsonpy.py,v 1.4 2014/05/21 19:51:11 weiwang Exp $
##
"""
| This file is part of the c9r package
| Copyrighted by Wei Wang <ww@9rivers.com>
| License: https://github.com/ww9rivers/c9r/wiki/License

Contains classes:

- JSON64
"""

import json
from base64 import b64decode, b64encode
from c9r.jsonpy import Thingy


class JSON64(Thingy):
    '''A storage device intended for user credentials.

    A set of keywords may be configured to base64 encode their values
    for output. The purpose is to obscure the value so that they are
    not completely in the clear.
    '''
    def_keys = [ 'password', 'pass', 'pw', 'key', 'secret', 'sharedsecret' ]

    def get(self, key, default=None):
        '''Get value with a given key.

        If the key is in the set of keys to be encoded, the return value is decoded.
        '''
        val = super(JSON64, self).get(key, default)
        if val and key in self.keys:
            try:
                val = b64decode(val)
            except:
                pass # Ignore error, assume the value is not encoded
        return val

    def __save__(self, path=None):
        if path:
            self._file = path
        self._changed = True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        '''Save the contents with 
        '''
        if self._file and self._changed:
            with open(self._file, 'w') as fp:
                json.dump(self.dict(), fp)

    def __init__(self, dconf=None, keys=None):
        self._file = dconf if isinstance(dconf, basestring) else None
        self._changed = False
        super(JSON64, self).__init__(dconf)
        if keys is None:
            self.keys = self.def_keys
        elif keys[0] == '+':
            self.keys = self.def_keys + keys[1:]
        else:
            self.keys = keys

    def __setitem__(self, key, val):
        '''Set value with a given key.

        If the key is in the set of keys to be encoded, the value is decoded.
        '''
        self._changed = True
        if not val is None and key in self.keys:
            val = b64encode(val)
        return super(JSON64, self).__setitem__(key, val)

if __name__ == '__main__':
    import doctest
    doctest.testfile('ustore-test.text')
