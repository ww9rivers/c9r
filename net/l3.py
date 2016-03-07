#!/usr/bin/env python
'''
$Id: l3.py,v 1.5 2015/12/04 14:57:29 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

import os, socket, struct
from c9r.pylog import logger


def default_gateway():
    """
    Read the default gateway directly from /proc/net/route.

    References:
    https://gist.github.com/1059982
    http://stackoverflow.com/questions/4904047/how-can-i-get-the-default-gateway-ip-with-python
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
    doctest.testfile('test/l3.txt')
