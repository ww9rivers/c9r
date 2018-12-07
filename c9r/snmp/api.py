#!/usr/bin/env python3

'''
This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2009-2015, Wei Wang. All rights reserved.
'''

from pysnmp.hlapi import *
import gettext, os, re, socket, string
from c9r.pylog import logger
t = gettext.gettext


def extend_environ(xset, xvar='PATH'):
    """
    Extend an environment variable, which defaults to "PATH", with a provided "xset" value.
    """
    if xset:
        os.environ[xvar] = ':'.join(set(os.environ.get(xvar, '').split(':'))|set(xset))

def nominal_speed(xrate):
    """
    Convert numerical speed (10000000) to nominal speed (10mbps).

    @param	rate	Numberical speed
    @return	Nominal speed.
    """
    xunit = ''
    if xrate >= 1000:
        xunit = 'k'
        xrate = round(xrate/1000)
        if xrate >= 1000:
            xunit = 'm'
            xrate = round(xrate/1000)
            if xrate >= 1000:
                xunit = 'g'
                xrate = round(xrate/1000)
    return "%d%sbps" % (xrate, xunit)


class Prefix:
    """
    MIB object tag (name) prefix.
    """
    def lower(self, tag):
        return self(tag.lower())

    def __call__(self, tag):
        return self.re.sub(self.rep, tag) if self.re else tag

    def __init__(self, xpre, replacement=''):
        self.re = 0
        if xpre:
            import re
            self.re = re.compile('^'+xpre.lower())
            self.rep = replacement


class SNMPAPI:
    """
    Interface to the Net-SNMP Python library with system wide information
    (version, communities, secrets, etc) configured.

    The Python Net-SNMP package does not provide a method to load extra MIBs.
    But, it does load MIBs from Net-SNMP's configured paths and through environment
    variables MIBDIRS and MIBS, it is possible to load extra MIB files. The caveat,
    however, is that they have to be loaded before any SNMP function is called.
    """
    config = 0          ## SNMPAPI configuration thrugh "SNMP API Settings"

    def get(self, xoid, idx=None):
        ''' SNMP-get a specified object. '''
        g = getCmd(self.engine, self.community(),
                   UdpTransportTarget((self.host, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
        return next(g)

    def get_bits(self, xoid):
        '''
        Get a BITS type object.

        @param	xoid	Object id.
        @returns	Array of the bits.
        '''
        snmp_set_quick_print(FALSE)
        xvals = split(" ", self.get_object(xoid, "BITS"))
        snmp_set_quick_print(TRUE)

        re1 = re.compile(r'^(\w+)\((\d+)\)$')
        re2 = re.compile(r'^(\D+)(\d+.*)$')
        re3 = re.compile(r'^(\d+)(000mbps)$')
        xbits = []
        for xval in xvals:
            xm = re1.match(xval)
            if len(xm) > 1:
                xr = re2.match(xm[1])
                xv = (xr[1]+xr[0]) if len(xr) > 1 else xm[1]
                xm = re3.match(xv)
                xbits.append(xm[0]+"gbps" if xm else xv)
        return xbits

    def get_integer(self, xoid):
        xi = self.get_object(xoid, "INTEGER")
        return int(xi) if xi else None

    def get_object(self, xoid, prefix=''):
        """
        Get a single value of a given object on this device.

        @param	xoid	ID of the object to get value for.
        @param	prefix	Optional prefix to remove from the value.
        @return Value of retrieved MIB object.
        """
        xo = self.get(xoid)
        logger.debug("SNMPAPI.get_object: oid = {0}, val = {1}".format(xoid, xo))
        return Prefix(prefix)(xo[0]) if xo and xo[0] else None

    def get_string(self, xoid):
        return self.get_object(xoid, "STRING")

    def set(self, xoid, xtype, xvalue):
        """
        Set an SNMP object in this device.
        """
        g = setCmd(SnmpEngine(),
                   CommunityData('public'),
                   UdpTransportTarget(('demo.snmplabs.com', 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386'))
        next(g)

    def set_host(self, host):
        '''
        Set the destination host (name or IP address).
        '''
        self.host = host

    def walk(self, xoid, context=''):
        """
        Walk a MIB object within an optional context.

        @param	xoid	MIB object id.
        @param	xctx	Optional context.
        @return A VarList of object(s) walked -- usually a table.
        """
        authdata = UsmUserData('usr-md5-none', 'authkey1')
        if context:
            self.S['Community'] += "@"+context
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in nextCmd(SnmpEngine(),
                                  UsmUserData('usr-md5-none', 'authkey1'),
                                  UdpTransportTarget(('demo.snmplabs.com', 161)),
                                  ContextData(),
                                  ObjectType(ObjectIdentity('IF-MIB'))):
            if errorIndication:
                print(errorIndication)
                break
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                break
            else:
                for varBind in varBinds:
                    print(' = '.join([x.prettyPrint() for x in varBind]))
                    
        vars = xoid if isinstance(xoid, netsnmp.VarList) else netsnmp.VarList(netsnmp.Varbind(xoid))

        '''
        Context index: Not sure if this is a Cisco specific extension to SNMP v1/v2c
        	or a industry defacto standard. SNMPv3, however, has its own mechanism for
        	per-context MIB indexing.
        xropw = SNMPAPI.config.v2.ro_community
        '''
        self.S.walk(vars)
        if context:
            self.S['Community'] = self.S['Community'][0:-(1+len(context))]
        return vars

    def walk_object(self, xoid, context=''):
        '''
        Walk through SNMP objects and fetch their values

        @param	xoid	Starting point of the walk -- an object ID.
        @param	context	Optional context.
        @return	An array of values.
        '''
        xvar = self.walk(xoid, context)
        xobj = {}
        for v in xvar:
            xobj[v.iid] = v.val
        logger.debug("SNMPAPI.walk_object: oid = %s, val = %s" % (xoid, xobj))
        return xobj

    def walk_table(self, xtable, mib='', prefix='', context=''):
        """
        Walk through an SNMP object table and build a table. The OID name
        is expected to be <table>.<entry>.<variable>.<index> and the
        table is build as (table[index].variable).

        @param	xtable	Object ID of the table.
        @param	mib	(Optional) MIB (file) name.
        @param  context (Optional) Context name.
        @return	The table built or cached in this device.
        """
        rex = Prefix(prefix)
        if mib:
            xtable = mib+"::"+xtable
        if xtable in self.mib:
            return self.mib[xtable]

        xent = self.walk(xtable, context)
        xt = {}
        if xent:
            for xv in xent:
                if not xv.iid in xt:
                    xt[xv.iid] = {}
                xt[xv.iid][rex.lower(xv.tag)] = xv.val
        self.mib[xtable] = xt
        return xt

    @staticmethod
    def __add_MIB(mibs):
        '''Extend MIBS environment variable for MIB-loading, if given
        "mibs" has a True value.'''
        extend_environ(mibs,'MIBS')

    @staticmethod
    def __add_MIB_path(mibdirs):
        '''Extend MIBDIRS environment variable for MIB-loading, if given
        "mibdirs" has a True value.'''
        extend_environ(mibdirs,'MIBDIRS')

    def __init(self, **kwargs):
        '''
        Run-once initialization to configure this object.
        '''
        xc = kwargs.get('session')
        if not xc:
            raise Exception(t('SNMPAPI.config not found!'))
        domains = xc.get('domain')
        if isinstance(domains, str):
            xc.domain = domains.split("\r\n")
        logger.debug("SNMPAPI.__init: config({0}) = {1}".format(type(xc), xc))
        SNMPAPI.config = xc

    def __init__(self, xdev=None, **kwargs):
        '''
        Initialize the SNMP API, with session (self.S).

        @param xdev    May be either another SNMPAPI object, or a host (name or IP).
        @param kwargs  Arguments for netsnmp.Session.

        In case 'xdev' is another SNMP object, its session information is copied.

        Otherwise, i.e., 'xdev' is a host, 
        '''
        logger.debug("SNMPAPI.__init__: xdev = %s" % (xdev))
        if isinstance(xdev, SNMPAPI):
            self.engine = xdev.engine
            self.host = xdev.host
        else:
            SNMPAPI.__add_MIB_path(kwargs.get('mibdirs'))
            SNMPAPI.__add_MIB(kwargs.get('mibs'))
            if not SNMPAPI.config:
                self.__init(**kwargs)
            # HACK to accomondate SNMPAPI.config being c9r.jsonpy.Thingy:
            config = SNMPAPI.config
            config = dict(config if isinstance(config, dict) else config.dict())
            self.host = xdev
            logger.debug('New session: SNMPAPI.config = {0}'.format(config))
            self.engine = SnmpEngine()
        self.mib = {}

if __name__ == '__main__':
    import doctest, os
    if 'DEBUG' in os.environ:
        import logging, c9r.pylog
        c9r.pylog.set_level(logging.DEBUG)
    doctest.testfile('test-snmpapi.txt')
