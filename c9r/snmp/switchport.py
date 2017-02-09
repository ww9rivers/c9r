#!/usr/bin/env python
'''
$Id: switchport.py,v 1.3 2016/03/28 15:07:15 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html
'''

import portinfo


class SwitchPort(PortInformation):
    '''
    Set interface property using 'ifIndex'.
    '''
    xstval = { up: '1', down: '2' }
    xsttxt = [ 'up', 'down' ]

    def set_if(self, xoid, xtype, xvalue, xsfx = ''):
        return self.set('.'.join([xoid, self.ifindex, xsfx]), xtype, xvalue)

    def set_port(self, xoid, xtype, xvalue):
        '''
        Set port property using Cisco's 'portindex'.
        '''
        return self.set('.'.join([xoid, self.port]), xtype, xvalue)

    def set_alias(self, xalias):
        '''
        IF-MIB::ifAlias
        '''
        return self.set_if('.1.3.6.1.2.1.31.1.1.1.18', 's', xalias)

    def set_speed(self, xspeed, xduplex, xauto):
        xc = self.dclass
        if getattr(xc, 'set_speed'):
            return xc.set_speed(xthis, xspeed, xduplex, xauto)
        raise Exception("Device type '{0}' does not support setting port speed".format(xc.model.name))

    def set_status(self, xst):
	'''
        Turn the port status to administratively up or down.

	@param	xst	Status to set to. Must be (up, 1, down, 2).
	@return	true, if successful Or
		false, if failed.
        '''
        xst = xstval[xst]	#	IF-MIB::ifAdminStatus
        if xst and self.set_if('.1.3.6.1.2.1.2.2.1.7', 'i', xst):
            self.enabled = xsttxt[xst-1]
            return true
        return false

	def set_vlan(self, xvlan):
            '''
            CISCO-VLAN-MEMBERSHIP-MIB::vmVlan
            '''
            return self.set_if('.1.3.6.1.4.1.9.9.68.1.2.2.1.2', 'i', xvlan)

    def __init__(self, xp):
	'''
        SwitchPort constructor.

        Takes an object with the switch port's (ip_addr, ifindex, port)
        information to instantiate this object.

	@param	xp	A PortInformation object.
        '''
        PortInformation.__init__(self, xp.ip_addr, xp.ifindex, xp.port, xp)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
