#!/usr/bin/python
#
# $Id: spyder.py,v 1.1 2015/04/17 21:21:09 weiwang Exp $
#
# This program is licensed under the GPL v3.0, which is found at the URL below:
#	http://opensource.org/licenses/gpl-3.0.html
#
# Copyright (c) 2015, Wei Wang, All rights reserved.

from c9r.app import Command
from c9r.net import l3
from c9r.pylog import logger


class App(Command):
    '''App to track a device by MAC address or IP address.
    '''
    def __call__(self):
        gw = l3.default_gateway()
        for ip in self.args:
            logger.debug('Tracking down: {0}'.format(ip))


if __name__ == "__main__":
    app = App()
    if app.dryrun:
        import doctest
        doctest.testfile('test/ut.txt')
        app.exit_dryrun()
    app()
