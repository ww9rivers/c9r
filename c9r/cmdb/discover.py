#!/usr/bin/env python
'''
$Id: discover.py,v 1.2 2016/03/28 15:07:15 weiwang Exp $


This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

import gettext, logging, sys
from cisco.cdp import CDP
from c9r.app import Command
from c9r.cmdb.model import CMDB
from c9r.net import l3


class Discover(Command):
    def __call__(self):
        print(format(self.seeds))

    def __init__(self):
        Command.__init__(self)
        xc = self.CONF
        seeds = getattr(xc, 'seeds', [])
        if not seends():
            gws = l3.default_gateway()
            if isinstance(gws, str):
                seeds.append(gws)
            else:
                seeds.append(*gws)
        self.seeds = seeds


if __name__ == '__main__':
    '''
    To run the doctests: Will test with doctest.testfile().
    '''
    import doctest, os
    from twisted.python import log
    if 'DEBUG' in os.environ:
        log.startLogging(sys.stderr)
    doctest.testfile('test-discover.txt')
