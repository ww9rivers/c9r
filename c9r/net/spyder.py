#!/usr/bin/python
'''
$Id: spyder.py,v 1.2 2016/03/07 16:00:45 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

from c9r.app import Command
from c9r.net import l3, issh
from c9r.pylog import logger
from cisco.cli import cdp

def_gw = l3.default_gateway()


class Main(Command):
    '''Starting with the default gateway devices on the localhost, assuming
    that it is a router on the network, this tool crawls the local network
    following layer 2 connections, using command line over SSH connections
    to the devices.
    '''
    def_conf = [ '~/.etc/nss/spyder-conf.json' ]

    def __call__(self):
        logger.debug('Default gateway = {0}'.format(def_gw))
        cmd = cdp.details()
        ssh = issh.SecureShell(def_gw)
        _,result = ssh.run(cmd.command)[0]
        # Parse the result next
        result = cmd.parse(result)
        print(result)


def main():
    app = Main()
    if app.dryrun:
        import doctest
        doctest.testfile('test/spyder.text')
        exit(0)
    app()

if __name__ == "__main__":
    main()
