#!/usr/bin/env python3
##

"""
| This file is part of the c9r package
| Copyrighted by Wei Wang <ww@9rivers.com>
| License: https://github.com/ww9rivers/c9r/wiki/License

Contains classes:

- Null
- Thingy
"""

import json
import collections


class Null(object):
    '''
    A null object, to get the inner __dict__.
    '''
    def dict(self):
        '''Return self as a dict -- the inner dict.'''
        return self.__dict__

    def get(self, name, default=None):
        '''Get the value of an attribute with (name).'''
        return self.__dict__.get(name, default)

    def items(self):
        '''Retrieve items in this object as a list of 2-tuples.'''
        return self.__dict__.items()

    def iteritems(self):
        return iter(self.__dict__.items())

    def keys(self):
        return list(self.__dict__.keys())

    def update(self, data):
        '''Update this object with attribute/value pairs given in a dict.'''
        if data:
            self.__dict__.update(dict(data))

    def __getitem__(self, name):
        return self.__dict__.__getitem__(name)

    def __iter__(self):
        return iter(self.__dict__)

    def __repr__(self):
        '''
        Get a string representation of this object.
        '''
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __str__(self):
        '''Encode self in JSON format.'''
        return self.__dict__.__str__()

    __getattr__ = get
    __setattr__ = __setitem__


'''
http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
'''
class Thingy(Null):
    '''
    Build a Python object with given parameters as attributes.

    @param dconf        Optional default configuration file name, or a readable object.
    @param defval       Optional default values, that is fed to dict() for initializing this object.
    '''
    def __init__(self, dconf=None, defval=None):
        if isinstance(dconf, str):
            newconf = load_file(dconf, defval)
        elif hasattr(dconf, 'read') and isinstance(dconf.read, collections.Callable):
            newconf = load(dconf, defval)
        elif isinstance(dconf, Null):
            newconf = dconf.dict()
        elif not dconf is None:
            newconf = dict(dconf)
        elif not defval is None:
            newconf = dict(defval)
        else:
            newconf = dict()
        for xk, xv in newconf.items():
            if isinstance(xv, dict):
                xv = Thingy(xv)
            newconf[xk] = xv
        self.__dict__.update(newconf)

def load(fp, defval=None):
    '''
    Load an IO object (fp) that holds JSON data.

    Optionally, default values may be specified in (defval).    
    '''
    if defval is None:
        defval = dict()
    newconf = dict(defval.dict() if isinstance(defval, Null) else defval)
    newconf.update(json.load(fp, object_hook=_decode_dict))
    return newconf

def load_file(fname, defval=None):
    '''
    Load a file with the given file name (fname), containing JSON data.

    Optionally, default values may be specified in (defval).
    '''
    return load(open(fname, 'r'), defval)

# Functions for object_hook used with json_load(), based on:
#    http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-unicode-ones-from-json-in-python/
def _decode_dict(data):
    if isinstance(data, list):
        return _decode_list(data)
    rv = {}
    for key, value in data.items():
        if isinstance(value, list):
           value = _decode_list(value)
        elif isinstance(value, dict):
           value = _decode_dict(value)
        rv[key] = value
    return rv

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

if __name__ == '__main__':
    import doctest
    doctest.testfile('tests/jsonpy.test')
