#!/usr/bin/env python
##
## $Id: jsonpy.py,v 1.3 2014/03/27 20:38:27 weiwang Exp $
##
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2011, 9Rivers.NET, LLC
## All rights reserved.

import json


class Null(object):
    '''
    A null object, to get the inner __dict__.

    >>> nx = Null()
    >>> nx.items()
    []
    >>> nx.__repr__()
    "<class '__main__.Null'>({})"
    >>> nx.__str__()
    '{}'
    >>> nx.new_attr = 'abcde'
    >>> nx.new_attr
    'abcde'
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
        return self.__dict__.iteritems()

    def update(self, data):
        '''Update this object with attribute/value pairs given in a dict.'''
        self.__dict__.update(data)

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

    >>> xo = Thingy(dict(a='aaa', b='bbb'))
    >>> xo.a
    'aaa'
    >>> xo.items()
    [('a', 'aaa'), ('b', 'bbb')]
    >>> from StringIO import StringIO
    >>> x1 = Thingy(StringIO('{ "a" : "A-value", "b" : "B-value" }'))
    >>> x1.b
    'B-value'
    >>> isinstance(x1, dict)
    False
    >>> isinstance(x1, object)
    True
    >>> isinstance(x1, Null)
    True
    '''
    def __init__(self, dconf={}, defval={}):
        if isinstance(dconf, basestring):
            newconf = load_file(dconf, defval)
        elif hasattr(dconf, 'read') and callable(dconf.read):
            newconf = load(dconf, defval)
        elif isinstance(dconf, Null):
            newconf = dconf.dict()
        else:
            newconf = dict(dconf if dconf else defval)
        for xk, xv in newconf.iteritems():
            if isinstance(xv, unicode):
                xv = xv.encode('utf-8')
            elif isinstance(xv, dict):
                xv = Thingy(xv)
            newconf[xk] = xv
        self.__dict__.update(newconf)

def load(fp, defval={}):
    '''
    Load an IO object (fp) that holds JSON data.

    Optionally, default values may be specified in (defval).    
    '''
    newconf = dict(defval.dict() if isinstance(defval, Null) else defval)
    newconf.update(json.load(fp, object_hook=_decode_dict))
    return newconf

def load_file(fname, defval={}):
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
    for key, value in data.iteritems():
        if isinstance(key, unicode):
           key = key.encode('utf-8')
        if isinstance(value, unicode):
           value = value.encode('utf-8')
        elif isinstance(value, list):
           value = _decode_list(value)
        elif isinstance(value, dict):
           value = _decode_dict(value)
        rv[key] = value
    return rv

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

if __name__ == '__main__':
    import doctest
    doctest.testmod()
