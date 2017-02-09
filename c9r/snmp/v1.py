#!/usr/bin/env python
'''
$Id: api.py,v 1.5 2015/07/23 16:03:59 weiwang Exp $

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2009-2015, Wei Wang. All rights reserved.
'''

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
        return self.S.get(netsnmp.VarList(netsnmp.Varbind(xoid, idx)))

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
        vars = netsnmp.VarList(netsnmp.Varbind(xoid, None, xvalue, xtype))
        if self.S.set(vars):
            return True
        raise Exception("SNMPAPI::set failed: '%s', '%s', '%s'" % (xoid, xtype, xvalue))

    def set_host(self, host):
        '''
        Set the destination host (name or IP address).
        '''
        self.S.DestHost = host

    def walk(self, xoid, context=''):
        """
        Walk a MIB object within an optional context.

        @param	xoid	MIB object id.
        @param	xctx	Optional context.
        @return A VarList of object(s) walked -- usually a table.
        """
        vars = xoid if isinstance(xoid, netsnmp.VarList)\
            else netsnmp.VarList(netsnmp.Varbind(xoid))

        '''
        Context index: Not sure if this is a Cisco specific extension to SNMP v1/v2c
        	or a industry defacto standard. SNMPv3, however, has its own mechanism for
        	per-context MIB indexing.
        xropw = SNMPAPI.config.v2.ro_community
        '''
        if context:
            self.S['Community'] += "@"+context
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
            import copy
            self.S = copy.copy(xdev.S)
        else:
            SNMPAPI.__add_MIB_path(kwargs.get('mibdirs'))
            SNMPAPI.__add_MIB(kwargs.get('mibs'))
            if not SNMPAPI.config:
                self.__init(**kwargs)
            # HACK to accomondate SNMPAPI.config being c9r.jsonpy.Thingy:
            config = SNMPAPI.config
            config = dict(config if isinstance(config, dict) else config.dict())
            config['DestHost'] = xdev
            logger.debug('New session: SNMPAPI.config = {0}'.format(config))
            self.S = netsnmp.Session(**config)
        self.mib = {}

if __name__ == '__main__':
    import doctest
    doctest.testfile('test/v1.txt')
