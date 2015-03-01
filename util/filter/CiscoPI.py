#! /usr/bin/env python
#
# $Id: cisco.py,v 1.4 2015/01/08 20:45:56 weiwang Exp $
#

import re
from c9r.util.filter import Filter
from c9r.pylog import logger
from cisco.cli.port import nickname


class Normalizer(Filter):
    '''Cisco Prime Infrastructure (ciscopi) data normalizer.
    Cisco PI device report header:

    Last Seen,MAC Address,Vendor,IP Address,Device IP Address,Port,VLAN ID,802.11 State,
    Protocol,Endpoint Type,User,Connection Type,Last Session Length,Connected Interface,
    Access Technology Type
    '''
    remac = re.compile('[\.\-:]')  # 1a:2b:3c:4d:5e:6f
    retime = re.compile('\W+')     # 1 days 2 hrs 35 min 55 sec
    vendor_map = {
        'hewlett-packard': 'HP',        
        }

    def next(self):
        '''Interface function to produce the next piece of data for this filter.
        '''
        return self.normalize(Filter.next(self))

    def normalize(self, data):
        '''Here the data fields will be normalized before returned:

        o       MAC addresses are rid of delimiters;
        o       Values such as "Unknown" and "Not Supported" are removed;
        o       /Last Session Length/ values are converted to number of seconds;
        o       /User/ IDs are normalized to "domain/userid" format, also handing
                (wrongly-)escaped special characters embedded.
        '''
        for xk in [ 'APMACAddress', 'MACAddress' ]:
            xv = data.get(xk, '')
            if len(xv) > 12:
                data[xk] = ''.join(self.remac.split(xv)).lower()
        for xk in [ 'EndpointType', 'Vendor' ]:
            xv = data.get(xk, '')
            if xv == 'Unknown':
                data[xk] = ''
            elif len(xv) > 0:
                data[xk] = xv.strip()
        #
        # Wi-Fi tracking data:
        #
        for xk in [ 'CCX', 'E2E' ]:
            if data.get(xk, '') == 'Not Supported':
                data[xk] = ''
        it = iter(self.retime.split(data['LastSessionLength']))
        sec = 0
        for x in it:
            xsec = 0
            try:
                ut = next(it)
                xsec = int(x)*{ 'days': 86400, 'hrs': 3600, 'min': 60, 'sec': 1 }[ut]
            except KeyError:
                logger.error('Invalid time unit: {0}'.format(ut))
            except ValueError:
                logger.error('Invalid time value: {0}'.format(x))
            except StopIteration:
                pass
            sec += xsec
        data['LastSessionLength'] = sec
        #
        # Normalize vendor names
        #
        vendor = self.vendor_map.get(data.get('Vendor', '').lower())
        if vendor:
            data['Vendor'] = vendor
        # Process 'User' ID:
        #-- Hacky but no better way: Must deal with '\n', '\t' individually so not to
        #   convert '\' to '\\'.
        #-- Normalize to "domain/userid" format
        uid = data.get('User', '')
        if uid:
            for xt in [ [ '\n', '\\n' ], [ '\r', '\\r' ], ['\t', '\\t' ] ]:
                uid = uid.replace(xt[0], xt[1])
            uid = uid.replace('\\', '/', 1)
        data['User'] = uid
        port = data.get('InterfaceName')
        if port:
            data['InterfaceName'] = port = nickname(port)
            if not 'Port' in data:
                data['Port'] = port
        return data


class Wired(Normalizer):
    '''Cisco Prime Infrastructure (ciscopi) wired report selective filter.

    Exception: StopIteration is raised when data is exhausted.
    '''
    def is_wired(self, data):
        '''Test if given data set is a wired connection.
        '''
        return data.get('ConnectionType') == 'Wired'

    def next(self):
        '''Return the next wired connection record.
        '''
        while True:
            data = Filter.next(self)
            if self.is_wired(data):
                logger.debug('Data is wired: {0}'.format(data))
                return self.normalize(data)


class Wireless(Wired):
    '''Cisco Prime Infrastructure (ciscopi) wireless report selective filter.

    Exception: StopIteration is raised when data is exhausted.
    '''
    def next(self):
        '''Return the next wireless connection record.
        '''
        while True:
            data = Filter.next(self)
            if not self.is_wired(data):
                return self.normalize(data)


def test():
    '''Unit test for this filter module.
    '''
    import doctest
    import c9r.app
    class TestApp(c9r.app.Command):
        def __call__(self):
            doctest.testfile('test/cisco.test')
    TestApp()()


if __name__ == '__main__':
    import gevent
    tasks = [ gevent.spawn(test) ]
    gevent.joinall(tasks)
