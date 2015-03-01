#!/usr/bin/env python
##
## $Id: mac.py,v 1.1 2012/10/15 20:54:09 weiwang Exp $
##
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2012, 9Rivers.NET, LLC.  All rights reserved.

import re


class MACFormat:
    """
    Convert a given string, assumed to be a valid MAC address, to specific format.

    Raises a ValueError exception if the MAC address is invalid.

    Tests:

    >>> MACFormat.none('AA.BB.CC.DD.EE.FF')
    'aabbccddeeff'
    >>> MACFormat.dash('1122.3344.5566')
    '11-22-33-44-55-66'
    >>> MACFormat.ieee('1122.3344.5566')
    '11:22:33:44:55:66'
    >>> MACFormat.cisco('11:22:33:44:55:66')
    '1122.3344.5566'
    """
    delims = re.compile("[^0-9a-f]")

    @staticmethod
    def _reorg(mac, delim):
        mx = MACFormat.none(mac)
        if len(mx) != 12:
            raise ValueError("Invalid MAC: "+mac)
        return mx[:2]+delim+mx[2:4]+delim+mx[4:6]+delim+mx[6:8]+delim+mx[8:10]+delim+mx[10:]

    @staticmethod
    def asis(mac):
        ''' Default: No format change. '''
        return mac

    @staticmethod
    def cisco(mac):
        ''' 1122.3344.5566 '''
        mx = MACFormat.none(mac)
        if len(mx) != 12:
            raise ValueError("Invalid MAC: "+mac)
        return mx[:4]+'.'+mx[4:8]+'.'+mx[8:]

    @staticmethod
    def dash(mac):
        ''' 11-22-33-44-55-66 '''
        return MACFormat._reorg(mac, '-')

    @staticmethod
    def ieee(mac):
        ''' 11:22:33:44:55:66 '''
        return MACFormat._reorg(mac, ':')

    @staticmethod
    def none(mac):
        ''' 112233445566 '''
        str = ''
        for x in MACFormat.delims.split(mac.lower()):
            str += x
        return str


if __name__ == '__main__':
    import doctest
    doctest.testmod()
