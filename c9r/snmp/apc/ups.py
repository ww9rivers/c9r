#!/usr/bin/env python
'''
$Id: api.py,v 1.1 2013/02/19 14:46:18 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2013, 9Rivers.NET, LLC.
All rights reserved.
'''

from c9r.snmp import api

class PowerNet(api.SNMPAPI):
    '''Class for APC UPS devices' SNMP PowerNet-MIB objects.'''

    def __init__(self, ip, **kwargs):
        '''Initialize a PowerNet node, with the given IP address in "ip".

        Optional arguments accepted by c9r.snmp.api.SNMPAPI are accepted in "kwargs".
        '''
        # Make sure the PowerNet-MIB is loaded:
        api.SNMPAPI.__add_MIB('PowerNet-MIB')
        SNMPAPI.__init__(self, ip, **kwargs)

if __name__ == '__main__':
    import doctest, os, sys
    if 'DEBUG' in os.environ:
        log.startLogging(sys.stderr)
    doctest.testfile('test-ups.txt')
