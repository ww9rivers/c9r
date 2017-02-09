#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
        http://opensource.org/licenses/gpl-3.0.html

An command that uses SSH to compare a remotely file to a local copy
'''

import os
from c9r import app, jsonpy

def_etc = os.path.join(os.environ.get('HOME', ''), '.etc')


class Diffr(app.Command):
    def_hosts = os.path.join(def_etc, 'hosts.json')
    def_conf = [
        os.path.join(def_etc, 'deploy-conf.json'),
        '.deploy-conf.json'    # Deployment configuration
        ]

    def __call__(self):
        '''A command that uses SSH to compare a remotely file to a local copy.

        This utility basically uses SSH and GNU diff in this way:

        ssh remote-host 'cat remote-file' | diff - local-file
        '''
        myhosts = jsonpy.Thingy(self.CONF.get('hosts', self.def_hosts))
        for hk, hc in myhosts.iteritems():
            if hk != '':
                print('%s = %s'%(hk, hc))
        pass

if __name__ == '__main__':
    Diffr()()
