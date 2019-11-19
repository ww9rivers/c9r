#!/usr/bin/env python
'''
$Id$

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2012,2013 9Rivers.net. All rights reserved.

#  A command line skeleton with basic command line parameter handleing.

Tests:

>>> from c9r.power.iq import RESTAPI as PowerIQ
>>> piq = PowerIQ('test-poweriq.json')
>>> piq.system_info()
>>> piq.datacenters()
'''

import json
import requests
from c9r.jsonpy import Thingy

class RESTAPI:
    '''Interface to Raritan PowerIQ REST API.

    Reference: http://www.raritan.com/help/power-iq/v4.0.0/en/index.htm#23679
    '''
    defaults = {
        "site":         "poweriq"
        }

    def get(self, uri, payload={}, header={}):
        headers = dict(header)
        headers.update({ 'Content-Type': 'application/json',
                         'Accept': 'application/json' })
        return requests.get(self.base+uri, auth=self.CONF.auth,
                            data=json.dumps(payload), headers=headers)

    def datacenters(self):
        return self.get("data_centers")

    def inlets(self):
        pass

    def outlets(self):
        return self.get('outlets')

    def pdus(self):
        return self.get('pdus')

    def sensors(self):
        return self.get('sensors')

    def outlet_readings(self):
        ''' GET /api/v2/outlet_readings

        Returns readings from multiple outlets.
        '''
        return self.get('outlet_readings')

    def outlet_readings_rollups(self, interval='hourly'):
        '''GET /api/v2/outlet_readings_rollups/hourly<interval>
        '''
        pass

    def system_info(self):
        return self.get('system_info')

    def __init__(self, conf):
        '''Initialize this object with configuration.'''
        self.CONF = Thingy(conf, RESTAPI.defaults)
        self.base = self.CONF.base+'api/v2/'


if __name__ == '__main__':
    import doctest
    doctest.testmod()
