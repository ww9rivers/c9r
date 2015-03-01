#!/usr/bin/env python
##
## $Id: l3.py,v 1.4 2014/07/10 22:23:47 weiwang Exp $
##
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2009 Regents of the University of Michigan.
## All rights reserved.
##
## Redistribution and use in source and binary forms are permitted
## provided that this notice is preserved and that due credit is given
## to the University of Michigan at Ann Arbor. The name of the University
## may not be used to endorse or promote products derived from this
## software without specific prior written permission. This software
## is provided ``as is'' without express or implied warranty.

import os, socket, struct
from c9r.pylog import logger


def default_gateway():
    """
    Read the default gateway directly from /proc/net/route.

    References:
    https://gist.github.com/1059982
    http://stackoverflow.com/questions/4904047/how-can-i-get-the-default-gateway-ip-with-python

    >>> if 'DEBUG' in os.environ:
    ...     import logging, c9r.pylog
    ...     c9r.pylog.set_level(logging.DEBUG)
    >>> default_gateway() != ''
    True
    """
    if os.name == 'nt':
        # Windows:
        import wmi
        gw = {}
        for dev in wmi.WMI().query("select IPAddress,DefaultIPGateway from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE"):
            gw[dev.IPAddress[0]] = dev.DefaultIPGateway[0]
        return gw

    for line in open("/proc/net/route"):
        fields = line.strip().split()
        if fields[1] == '00000000' and (int(fields[3], 16) & 2):
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

def get_lan_ip():
    '''http://stackoverflow.com/questions/11735821/python-get-localhost-ip

    >>> ip = get_lan_ip()
    >>> logger.debug('IP = %s'%(ip))
    >>> ip is None
    False
    '''
    if os.name != "nt":
        import fcntl
        import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

    ip = socket.gethostbyname(socket.gethostname())
    logger.debug('Hostname IP = %s'%(ip))
    if not ip.startswith("127.") or os.name == "nt":
        return ip
    for ifname in interfaces():
        if not ifname.startswith('lo'):
            try:
                return get_interface_ip(ifname)
            except IOError as xerr:
                logger.debug(format(xerr))
    return None

def interfaces():
    '''Return a list of network interfaces -- works in Linux only for now.

    >>> len(interfaces()) > 0
    True
    '''
    if os.access('/proc/net/dev', os.R_OK):
        return [ line.split(':')[0].strip().lower()
                 for line in open('/proc/net/dev', 'r') if ':' in line ]
    return [ "eth0", "eth1", "eth2",
             "wlan0", "wlan1", "wifi0",
             "ath0", "ath1", "ppp0", ]

if __name__ == '__main__':
    '''
    To run the doctests: Will test with doctest.testfile().
    '''
    import doctest
    doctest.testmod()
