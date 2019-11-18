#!/usr/bin/env python3
'''
$Id: jsonvar.py,v 1.2 2014/03/04 20:51:06 weiwang Exp $

This program is licensed under the BSD 2 license, a template of which
is found at the URL below:
	http://opensource.org/licenses/BSD-2-Clause
with:
     <OWNER> = Wei Wang
     <ORGANIZATION> = 9Rivers.net, LLC
     <YEAR> = 2012
'''

import json
from pydal import DAL, Field


class JsonVar:
    """
    An object that serializes and stores variable in JSON format.
    The Data Abstraction Layer (DAL) of web2py is used.

    Tests:

    >>> import time
    >>> vs = JsonVar('sqlite:///tmp/jsonvar.db')
    >>> vs.delete('x')
    >>> now = time.time()
    >>> vs.set('x', { 'time': now })
    >>> x = vs.get('x')
    >>> x['time'] == now
    True
    >>> vs.set('x', { 'time': round(now+10) })
    >>> y = vs.get('x')
    >>> y['time'] == round(now+10)
    True
    >>> x['time'] != y['time']
    True
    >>> vs.delete('x')
    >>> z = vs.get('x')
    >>> z == None
    True
    """
    default_store = 'sqlite://jsonvar.db'


    def delete(self, varname):
        '''
        Delete a variable and its value from the store.
        '''
        try:
            del self.cache[varname]
        except:
            pass
        self.db(self.db.variable.name == varname).delete()

    def get(self, varname):
        '''
        Retrieve and cache the value of a specified variable.
        '''
        try:
            return self.cache[varname]
        except KeyError:
            try:
                val = json.loads(self.db.variable(name=varname).value)
                self.cache[varname] = val
                return val
            except:
                pass
        return None

    def load(self, fname):
        '''
        Load/cache variable and values from a JSON file.
        '''
        self.cache.update(json.load(open(fname, 'r'), 'utf-8'))

    def set(self, varname, val):
        '''
        Set the value of a given variable.
        '''
        self.cache[varname] = val
        self.db.variable.update_or_insert(self.db.variable.name==varname,
            name=varname, value=json.dumps(val))

    def __init__(self, store=''):
        """
        Variable storage construction: 'store' is either a database name, or a
        DAL database with a 'variable' table which contains both (name, value)
        fields.
        """
        self.cache = {}
        if type(store) == str:
            if store == '':
                store = JsonVar.default_store
            self.db = DAL(store)
            self.db.define_table('variable',
                                 Field('name', 'string', length=128, unique=True),
                                 Field('value', 'text'))
        else:
            self.db = store


if __name__ == '__main__':
    import doctest
    doctest.testmod()
