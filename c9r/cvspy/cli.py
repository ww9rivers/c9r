#!/usr/bin/env python
'''
$Id: matrix.py,v 1.1 2013/02/19 21:11:31 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html
'''

import os, re
from subprocess import Popen, PIPE


class CVS:
    '''
    Object to interact with the CVS command line.
    '''
    _cvs = '/usr/bin/cvs'
    re_status = 'File:\s+(\S+)\s+Status:\s+(.+)$'

    def changes(self):
        '''
        Find out what are changed locally.
        '''
        rex = self.re['status']
        clist = []
        for status in self.run('status').readlines():
            match = rex.search(status)
            if match and match.group(2) == 'Locally Modified':
                clist.append(match.group(1))
        return clist

    def commit(self, message, docs=[]):
        self.run(['commit', '-m', message]+docs).read()

    def diff(self, doc):
        '''
        Run a 'cvs diff' on one given document.
        '''
        clist = []
        for change in self.run(['diff', doc]).readlines():
            clist.append(change[:-1])
        return clist

    def run(self, cmd):
        '''
        Run a given CVS command (cmd) and return its output.
        '''
        args = [self.tool]+([cmd] if isinstance(cmd, str) else cmd)
        return Popen(args, stdout=PIPE).stdout

    def __init__(self, conf={}):
        self.CONF = conf
        self.tool = conf.get('tool', self._cvs)
        self.re = {
            'status': re.compile(self.re_status)
            }
        wdir = getattr(conf, 'workspace', '')
        if wdir:
            os.chdir(wdir)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
