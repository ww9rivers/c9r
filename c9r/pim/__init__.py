#!/usr/bin/env python
#
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2012, 9Rivers.NET, LLC.  All rights reserved.

'''
Package as a configurable Privileged Information Manager module.
'''
import os, stat
from c9r.file.config import Config, TextPassword
from c9r.pylog import logger


class PIM(Config):
    '''App-scoped Pricleged Information Manaement module.
    '''
    def_conf = [ '/app/etc/pim-conf.json' ]
    def check_privilege(self, fname):
        '''Check if the file is readable to owner only.
        '''
        fst = os.stat(fname)
        if fst.st_mode & (stat.S_IROTH|stat.S_IRGRP) != 0:
            raise Exception("File '{0}' must be readable to owner only.".format(fname))

    def get(self, id, cpw=None):
        '''Get the credential for "id".
        '''
        pw = cpw or self[id].get('password')
        if pw is None: raise Exception("Password for id '{0}' not found.".format(id))
        logger.debug('Credential resolved for user ({0})'.format(id))
        return TextPassword(pw).cleartext()

    def __init__(self, conf=None):
        '''Initialize this object. Also: Check if the config files have proper access control.
        '''
        for xf in self.def_conf+(conf if type(conf) is list else [] if conf is None else [conf]):
            self.check_privilege(xf)
        Config.__init__(self, conf)

if __name__ == '__main__':
    import doctest
    doctest.testfile('test/pim.text')
