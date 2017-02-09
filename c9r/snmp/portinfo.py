#!/usr/bin/env python
'''
$Id: portinfo.py,v 1.3 2016/03/28 15:07:15 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html
'''

import re, snmpapi
from device import SNMPDevice
from c9r.pylog import logger



class PortInformation(SNMPDevice):
    """
    Information for a particular interface.

    CISCO-C2900-MIB:
        c2900PortDuplexState 
	c2900PortAdminSpeed

    CISCO-STACK-MIB
        portType
	portAdminSpeed
	portDuplex

    Tests:

    >>> import json, sys
    >>> xc = json.load(open('test-snmpapi-conf.json', 'r'), 'utf-8')
    >>> xs = xc['session']
    >>> snmp = PortInformation(xc['host'], xc['ifindex'], session=xs)
    >>> snmp.S.Version == xs['Version']
    True
    >>> snmp.S.Community == xs['Community']
    True
    >>> hostname = snmp.get_hostname()
    >>> hostname == xc['name']
    True
    >>> snmp.get_sysid() == xc['sysid']
    True
    """

    re_ifdescr = re.compile('([A-Za-z]+)\d+\/\d+')

    def get_cisco_vlanid(self):
        ''' VLAN id = CISCO-VLAN-MEMBERSHIP-MIB::vmVlan '''
	return self.get_integer('.1.3.6.1.4.1.9.9.68.1.2.2.1.2')

    def get_auto_speed(self):
        raise Exception('Device not classified')

    def get_counter32(self, xoid):
        return int(self.get_info(xoid, 'Counter32'))

    def get_duplex(self):
        raise Exception('Device not classified')

    def get_ifadminstatus(self):
        ''' Admin status: Up or Down = IF-MIB::ifAdminStatus '''
        return self.get_integer('.1.3.6.1.2.1.2.2.1.7')

    def get_ifalias(self):
        ''' Interface description = IF-MIB::ifAlias '''
        return self.get_info('.1.3.6.1.2.1.31.1.1.1.18', 'STRING')

    def get_ifinbroadcastpkts(self):
        ''' IF-MIB::ifInBroadcastPkts '''
        return self.get_counter32('.1.3.6.1.2.1.31.1.1.1.3')

    def get_ifinerrors(self):
        ''' Number of errors in = IF-MIB::ifInErrors '''
        return self.get_counter32('.1.3.6.1.2.1.2.2.1.14')

    def get_ifinmulticastpkts(self):
        ''' IF-MIB::ifInMulticastPkts '''
        return self.get_counter32('.1.3.6.1.2.1.31.1.1.1.2')

    def get_ifinucastpkts(self):
        ''' IF-MIB::ifInUcastPkts '''
        return  self.get_counter32('.1.3.6.1.2.1.2.2.1.11')

    def get_ifname(self):
	'''
        Retrieve IF-MIB::ifName of given interface.

	@return	Interface name as string.
	'''
        return self.get_string('.'.join([".1.3.6.1.2.1.31.1.1.1.1.", self.ifindex]))

    def get_ifoperstatus(self):
        ''' Operation status: Connected or not = IF-MIB::ifOperStatus '''
        return self.get_integer('.1.3.6.1.2.1.2.2.1.8')

    def get_ifoutucastpkts(self):
        ''' IF-MIB::ifOutUcastPkts '''
        return self.get_counter32('.1.3.6.1.2.1.2.2.1.17')

    def get_ifoutmulticastpkts(self):
        ''' IF-MIB::ifOutMulticastPkts '''
        return self.get_counter32('.1.3.6.1.2.1.31.1.1.1.4')

    def get_ifoutbroadcastpkts(self):
        ''' IF-MIB::ifOutBroadcastPkts '''
        return self.get_counter32('.1.3.6.1.2.1.31.1.1.1.5')

    def get_ifouterrors(self):
        ''' Number of errors out = IF-MIB::ifOutErrors '''
        return self.get_counter32('.1.3.6.1.2.1.2.2.1.20')

    def get_ifspeed(self):
        ''' Speed in BPS = IF-MIB::ifSpeed '''
        return int(self.get_info('.1.3.6.1.2.1.2.2.1.5', 'Gauge32'))

    def get_info(self, xoid, xpfx):
        return self.get_object('.'.join([xoid, self.ifindex]), xpfx)

    def get_integer(self, xoid):
        return int(self.get_info(xoid, 'INTEGER'))

    def get_port_integer(self):
        return int(self.get_object('.'.join([xoid, self.port]), 'INTEGER'))

    def guess_rates(self):
	'''
        Guess the data rates supported by this port from the interface description.

        @return	self.rates	Array of data rate descriptions.
	'''
        self.rates = []		#	IF-MIB::ifDescr
        xm = self.re_ifdescr.match(self.get_info(".1.3.6.1.2.1.2.2.1.2", 'STRING'))
        if xm:
            rate = xm.groups[0]
            if rate == 'GigabitEthernet':
                rate = '1gbps'
            elif rate == 'FastEthernet':
                rate = '100mbps'
            else:
                rate = '10mbps'
            self.rates.append(rate)

    def setattr(self, attr, fn, **opt):
        setattr(self, attr, opt[attr] if attr in opt else fn(self))

    def __init__(self, xdev, xif, **kwargs):
        '''
        PortInformation constructor.

        The 'rates' information is set in the optional auto_speed() method in
        the device class object.

	@param	xip	IPv4 address of the device.
	@param	xif	IF-MIB::ifIndex of the port.
	@param	kwargs	Optional 
	@param	kwargs[port]	Port number, for older Cisco devices
        '''
        self.ifindex = xif	## Interface index
        SNMPDevice.__init__(self, xdev, **kwargs)
        self.port = kwargs['port'] if 'port' in kwargs else None

        self.setattr('speed', lambda x: snmpapi.nominal_speed(x.get_ifspeed()), **kwargs)
        self.setattr('desc', lambda x: x.get_ifalias(), **kwargs)
        self.setattr('enabled', lambda x: x.get_ifadminstatus(), **kwargs)
        self.setattr('connected', lambda x: x.get_ifoperstatus(), **kwargs)
        self.setattr('vlan', lambda x: x.get_cisco_vlanid(), **kwargs)

        # Interface stats:
        self.packets_in = self.get_ifinucastpkts()+self.get_ifinmulticastpkts()+self.get_ifinbroadcastpkts()
        self.packets_out = self.get_ifoutucastpkts()+self.get_ifoutmulticastpkts()+self.get_ifoutbroadcastpkts()
        self.errors_in = self.get_ifinerrors()
        self.errors_out = self.get_ifouterrors()

        # Data rates supported by the port
        self.guess_rates()

        # Full or half duplex
        self.setattr('duplex', lambda x: x.get_duplex(), **kwargs)
        # (MAU-MIB::ifMauAutoNegAdminStatus)
        self.setattr('auto', lambda x: x.get_auto_speed(), **kwargs)


if __name__ == '__main__':
    import doctest, os
    if 'DEBUG' in os.environ:
        import logging
        import c9r.pylog
        c9r.pylog.set_level(logging.DEBUG)
    doctest.testmod()
