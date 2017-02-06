#!/usr/bin/python
#
#       $Id: cache.py,v 1.2 2015/06/01 15:00:12 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

from c9r.file.config import Config
from c9r.pylog import logger


class Cache(Config):
    '''An generic Cache with default settings and a __make__() interface.
    '''
    defaults = {
        'window': 2700,         # Window for caching: 45 min
        }
    def_conf = ['~/.etc/cache-conf.json']

    def clear(self, clear_all=True):
        '''Remove the entire content(s) in the cache.
        '''

    def clear_cache(self, dn, fns):
        '''
        '''

    def get(self, name):
        '''Get a named data from this cache.
        '''

    def put(self, name, data):
        '''Save given data into the cache with given name.
        '''
        raise 'Not implemented: {0}.put'.format(type(self))

    def __init__(self, conf=[], initconf=None):
        '''
        '''
        iconf = Cache.defaults
        iconf.update(initconf or {})
        Config.__init__(self, conf, initconf=iconf)

    @staticmethod
    def __make__(klass, conf=[], initconf=None):
        '''Create/make a Cache'ing class object.
        '''
        mn = klass.rsplit('.', 1)
        return getattr(__import__(mn[0], fromlist=mn[1:]), mn[1])(conf, initconf)


if __name__ == '__main__':
    import doctest
    doctest.testfile('test/cache.test')
