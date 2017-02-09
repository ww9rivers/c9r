#!/usr/bin/env python
'''
$Id$

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html
'''

from c9r.pylog import logger


class DeviceAPI:
    '''
    DeviceAPI: Base class module to formalize interface to device class module.
    '''
    def schema():
        raise Exception('%s (Line: %s): Device API module schema not defined' % (self.__file__, self.__line__))

    def get_device_class(self):
        """
        Get the class of this device.
        """
        if self.klass:
            return self.klass

        if not self.set_device_class():
            # Try to guess device class -- self.sysid should be set from above:
            #:    CISCO-STACK-MIB	=> Stackable
            #:    Otherwise default	=> CiscoIOS
            self.classid = 2 if self.sysid and ("CISCO-STACK-MIB::" in self.sysid) else 1
            if not self.set_device_class():
                raise Exception("Cannot determine device class: sysObjectID = "+self.sysid)
        return self.klass

    def set_device_class(self):
	'''
        Set the device class of a given SNMPDevice object.

        @param	xdev		Reference to an SNMPDevice object.
	@return	TRUE if the device class exists, with $xdev.model containing the following:
                name		The model name of the device.
                duplexOID	SNMP OID for port duplex status.
                classid		Device class identifier.
                class		Device class name.
        '''
        xsysid = "Not found"
        if not self.klass:
            if self.classid:
                xres = db_query('SELECT classid,duplexOID,class FROM snmp_devmodule WHERE classid=%d',
                                self.classid)
            else:
                xsysid = self.get_sysid()
                xres = db_query('''SELECT name, duplexOID, classid, class
						FROM snmp_devclass, snmp_devmodule
						WHERE sysobjectid="%s" AND dcid=classid''', xsysid)
                xmodel = db_fetch_object(xres)
                if xmodel.classid:
                    self.classid = xmodel.classid
                unset(xmodel.classid)

                if class_exists(xmodel.klass)\
                        or module_load_include('inc', 'snmpapi', xmodel.klass) != False:
                    self.klass = xmodel.klass(xmodel)
                else:
                    logger.info("Failed to load device class module '{klass}', portman='{path}'"\
                                    .format(**dict(
                                klass=xmodel.klass,
                                path=drupal_get_path('module', 'portman'))))
        else:
            self.sysid = xsysid
            logger.info("Failed to clasify device '!ip' (sysid = '{sysid}', classid = '{classid}')"\
                            .format(**dict(
                        ip=self.ip_addr,
                        sysid=xsysid,
                        classid=self.classid)))
        return self.klass
