#!/usr/bin/env python
##
## $Id: mac.py,v 1.3 2015/10/26 20:11:46 weiwang Exp $
##
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2012, 9Rivers.NET, LLC.  All rights reserved.

import re

delims = re.compile("[^0-9a-f]")


class InvalidMACAddress(Exception):
    '''Exception for invalid MAC address.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Invalid MAC address: {0}'.format(self.value)


def split(mac, seg=2):
    '''To handle missing leading 0's in the given MAC address.
    '''
    x = MACFormat.none(mac)
    return [ x[i:i+seg] for i in range(0, 12, seg) ]


class MACFormat:
    """
    Convert a given string, assumed to be a valid MAC address, to specific format.

    Raises a ValueError exception if the MAC address is invalid.
    """
    @staticmethod
    def asis(mac):
        ''' Default: No format change. '''
        return mac

    @staticmethod
    def cisco(mac):
        ''' 1122.3344.5566 '''
        return '.'.join(split(mac, 4))

    @staticmethod
    def dash(mac):
        ''' 11-22-33-44-55-66 '''
        return '-'.join(split(mac))

    @staticmethod
    def ieee(mac):
        ''' 11:22:33:44:55:66 '''
        return ':'.join(split(mac))

    @staticmethod
    def none(mac):
        ''' 112233445566 '''
        x = delims.split(mac.lower())
        if len(x) == 6:
            return ''.join([('00'+xe)[-2:] for xe in x])
        if len(x) == 3:
            return ''.join([('0000'+xe)[-4:] for xe in x ])
        if len(x) == 1:
            return ('0'*12+x[0])[-12:]
        raise InvalidMACAddress(mac)


if __name__ == '__main__':
    import doctest
    doctest.testfile('test/mac.txt')
