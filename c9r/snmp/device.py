#!/usr/bin/env python
'''
$Id: device.py,v 1.2 2016/03/28 15:07:15 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html
'''

from snmpapi import SNMPAPI


class SNMPDevice(SNMPAPI):
    """
    Network device supporting SNMP.

    Tests:

    >>> import json
    >>> xc = json.load(open('test-snmpapi-conf.json', 'r'), 'utf-8')
    >>> xs = xc['session']
    >>> snmp = SNMPDevice(xc['host'], session=xs)
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
    def get_sysdescr(self):
	""" Get 'SNMPv2-MIB::sysDescr' """
        return self.get_string('.1.3.6.1.2.1.1.1.0')

    def get_sysid(self):
	""" SNMPv2-MIB::sysObjectID """
        return self.get_object('.1.3.6.1.2.1.1.2.0', 'OID')

    def get_hostname(self):
	""" SNMPv2-MIB::sysName """
        return self.get_string('.1.3.6.1.2.1.1.5.0')

    def get_location(self):
	""" SNMPv2-MIB::sysLocation """
        return self.get_string('.1.3.6.1.2.1.1.6.0')

    def walk_interfaces(self):
	""" Walking IF-MIB::ifTable """
	return self.walk_object(".1.3.6.1.2.1.2.2")

    def walk_ifName(self):
	""" Walking IF-MIB::ifName """
        return self.walk_object(".1.3.6.1.2.1.31.1.1.1.1")

    def walk_ifIndex(self):
	""" Walking IF-MIB::ifIndex """
	return self.walk_object(".1.3.6.1.2.1.2.2.1.1")

    def __init__(self, xdev, **kwargs):
	"""
        Constructing an SNMPDevice with given information.

        @param	xdev	IP address, or DNS name, of a device.
        @param	kwargs	Optional arguments:
                        class           device classfier.
                        version         SNMP version (1/2c/3)
                        community       SNMP community for version 1 and 2c.
        """
        SNMPAPI.__init__(self, xdev, **kwargs)

        if 'classifier' in kwargs:
            self.classifier = kwargs['classfier']
        if isinstance(xdev, SNMPDevice):
            self.classid = xdev.classid
            self.dclass = xdev.dclass


if __name__ == '__main__':
    import doctest
    doctest.testmod()
