#!/usr/bin/python
#
#       $Id: cache.py,v 1.1 2015/06/01 13:40:07 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

from pydal import DAL, Field
from time import time
from c9r.util.cache import Cache
from c9r.pylog import logger


class DBCache(Cache):
    '''An implementation of the c9r.file.cache.FileCache with PyDAL using
    database.
    '''
    defaults = {
        'db': 'sqlite://cache.db',      # Database URL
        }
    def_conf = ['~/.etc/cache-conf.json']

    def clear(self, clear_all=True):
        '''Remove the entire content(s) in the cache.
        '''
        db = self.db
        db((db.vars.id>=0) if clear_all else (db.vars.expires<time())).delete()

    def clear_cache(self, vset, names):
        '''
        '''

    def get(self, vset, name):
        '''Get a named data from this cache.
        '''
        db = self.db
        rows = db((db.vars.name==name)&(db.vars.expires<time())).select()
        return rows[0].value

    def put(self, vset, name, data):
        '''Save given data into the cache with given name.
        '''
        self.db.vars.insert(name=name, value=data, expires=time()+self.window)

    def __init__(self, conf=[], initconf=None):
        '''
        '''
        Cache.__init__(self, conf, initconf)
        self.db = DAL(self.config('db'))
        self.db.define_table('varset', Field('name'))
        self.db.define_table('vars',
                             Field('name'), Field('value', 'json'),
                             Field('varset'),
                             Field('expires', 'integer'),
                             primarykey=['varset', 'name'])
        self.window = int(self.config('window'))


if __name__ == '__main__':
    import doctest
    doctest.testfile('test/cache.test')
