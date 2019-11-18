#! /usr/bin/env python3

import re
from time import strftime, strptime
from c9r.net.mac import MACFormat
from c9r.util.filter import Filter
from c9r.pylog import logger
from c9r.cisco.cli.port import nickname

pi_timeformat = '%a %b %d %H:%M:%S %Z %Y'
sql_timeformat = "%b %d %Y %I:%M:%S%p"


class Normalizer(Filter):
    '''Cisco Prime Infrastructure (ciscopi) data normalizer.
    Cisco PI device report header:

    Last Seen,MAC Address,Vendor,IP Address,Device IP Address,Port,VLAN ID,802.11 State,
    Protocol,Endpoint Type,User,Connection Type,Last Session Length,Connected Interface,
    Access Technology Type

    ====
    The class data below may need to be made configurable in the future:
    '''
    retime = re.compile('(\d+)\s*([a-zA-Z]+)')  # 1 days 2 hrs 35 min 55 sec // 1days2hrs35min 55sec
    reclean = re.compile('[^\w\s]*') # Regex to clean up CSV field
    cleansub = ''
    vendor_map = {
        'apple,inc': 'Apple',
        'hewlett-packard': 'HP',
        'hewlett': 'HP',
        #'verifone,inc.': 'Verifone',
        'unknown': ''
        }

    def normalize(self, data):
        '''Here the data fields will be normalized before returned:

        o       MAC addresses are rid of delimiters;
        o       Values such as "Unknown" and "Not Supported" are removed;
        o       /Last Session Length/ values are converted to number of seconds;
        o       /User/ IDs are normalized to "domain/userid" format, also handing
                (wrongly-)escaped special characters embedded.
        '''
        for xk in [ 'APMACAddress', 'MACAddress' ]:
            xv = data.get(xk)
            if xv:
                data[xk] = MACFormat.none(xv)
        for xk in [ 'EndpointType' ]:
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
        try:
            it = self.retime.findall(data['LastSessionLength'])
        except Exception:
            it = []
        sec = 0
        for x in it:
            xsec = 0
            try:
                ui, ut = x
                xsec = int(ui)*{ 'days': 86400, 'hrs': 3600, 'min': 60, 'sec': 1 }[ut]
            except KeyError:
                logger.error('Invalid time unit: {0}'.format(ui))
            except ValueError:
                logger.error('Invalid time value: {0}'.format(ut))
            except StopIteration:
                pass
            sec += xsec
        if sec > 0:
            data['LastSessionLength'] = sec
        #
        # Normalize vendor names
        #
        vendor_name = data.get('Vendor', '')
        vendor = self.vendor_map.get(vendor_name.lower())
        if vendor is None:
            vendor = self.reclean.sub(self.cleansub, vendor_name)
        if vendor != vendor_name:
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

    def write(self, data):
        '''Normalize given data before writing to the pipe.
        '''
        data = self.normalize(data)
        return 0 if data is None else Filter.write(self, data)


class Wired(Normalizer):
    '''Cisco Prime Infrastructure (ciscopi) wired report selective filter.

    Exception: StopIteration is raised when data is exhausted.
    '''
    def is_filtered(self, data):
        '''Test if given data set is not a wired connection.
        '''
        return data.get('ConnectionType') != 'Wired'

    def write(self, data):
        '''Actually write the data if it is wired.
        '''
        if self.is_filtered(data):
            return 0
        return Normalizer.write(self, data)


class Wireless(Wired):
    '''Cisco Prime Infrastructure (ciscopi) wireless report selective filter.

    Exception: StopIteration is raised when data is exhausted.
    '''
    def is_filtered(self, data):
        '''Return True if this is not wireless connection record.
        '''
        return not Wired.is_filtered(self, data)


class TimeNormalizer(Normalizer):
    '''Convert time string from "Tue Mar 10 08:12:01 EST 2015"
    to "Mar 10 2015 8:12:01AM".
    '''
    def normalize(self, data):
        '''Normalize Cisco PI data, and convert "LastSeen" field to SQL time format.
        '''
        try:
            data['LastSeen'] = strftime(sql_timeformat, strptime(data['LastSeen'], pi_timeformat))
        except:
            pass
        return Normalizer.normalize(self, data)


class WiredSQL(TimeNormalizer, Wired):
    '''Filter for wired data and also convert timestamp to SQL format.
    '''


class WirelessSQL(TimeNormalizer, Wireless):
    '''Filter for wired data and also convert timestamp to SQL format.
    '''

class WirelessGuest(WirelessSQL):
    '''Filter for devices on one of the guest wireless networks.
    '''
    guest_SSIDs = [ 'MGuest-UMHS', 'MWireless-UMHS' ]
    def is_filtered(self, data):
        '''Filter the data if it is not wireless, or it is not on one of the guest SSID.
        '''
        return Wireless.is_filtered(self, data)\
            or not data.get('SSID') in self.guest_SSIDs


class WirelessUMHS(WirelessGuest):
    '''Filter for wireless devices on none of the guest wireless networks.
    '''
    def is_filtered(self, data):
        return Wireless.is_filtered(self, data)\
            or data.get('SSID') in self.guest_SSIDs


def test():
    '''Unit test for this filter module.
    '''
    import doctest
    from c9r import app
    class TestApp(app.Command):
        def __call__(self):
            doctest.testfile('tests/cisco.test')
    TestApp()()


if __name__ == '__main__':
    import gevent
    tasks = [ gevent.spawn(test) ]
    gevent.joinall(tasks)
