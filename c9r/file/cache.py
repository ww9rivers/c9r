#!/usr/bin/python
#
#       $Id: cache.py,v 1.4 2015/06/01 15:00:12 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

import os, os.path
from c9r.util import jso
from c9r.util.cache import Cache
import c9r.file.util as fu
from c9r.pylog import logger


class FileCache(Cache):
    '''Implementing a file-based configured cache for any data objects that
    may be JSON-ified.
    '''
    defaults = {
        'path': '~/tmp',
        }

    def clear(self, clear_all=True):
        '''Remove the entire content(s) in the cache.
        '''
        os.path.walk(self.top, FileCache.clear_cache, self)
        if clear_all:
            os.rmdir(self.top)

    def clear_cache(self, vset, fns):
        '''Clear entries (fns) in a given folder (vset).
        '''
        logger.debug('Deleting {0}/{1}'.format(vset, fns))
        for fn in fns:
            os.unlink(os.path.join(vset, fn))

    def path(self, name):
        '''Create a full path to file with given name.
        '''
        cname = os.path.normpath(name)
        cname = name if name[0] == os.sep else os.path.join(self.top, name)
        head, tail = os.path.split(cname)
        logger.debug('Path "{0}" split to {1} : {2}'.format(cname, head, tail))
        if tail != name and not os.path.isdir(head):
            logger.debug('Creating folder: {0}'.format(head))
            fu.forge_path(head)
        return cname

    def get(self, vset, name):
        '''Get a named data from this cache.
        '''
        cname = self.path(os.path.join(vset, name))
        if not os.access(cname, os.R_OK) or fu.modified_before(cname, self['window']):
            return None
        return jso.load_storage(cname)

    def put(self, vset, name, data):
        '''Save given data into the cache with given name.

        /vset/          Variable set. In this object, a subfolder name.
        /name/          Variable name.
        /data/          Variable value.
        '''
        jso.save_storage(data, self.path(os.path.join(vset, name)))

    def __init__(self, conf=[], initconf=None):
        iconf = FileCache.defaults
        iconf.update(initconf or {})
        Cache.__init__(self, conf, initconf=iconf)
        self.top = os.path.expanduser(self['path'])

if __name__ == '__main__':
    import doctest
    doctest.testfile('test/cache.test')
