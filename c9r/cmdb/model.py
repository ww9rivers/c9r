# -*- coding: utf-8 -*-
#
# $Id: model.py,v 1.2 2015/07/23 16:03:59 weiwang Exp $

from gluon.dal import DAL
from gluon.tools import Service, PluginManager, prettydate
from gluon.validators import IS_IN_SET


class CMDB(DAL):
    '''
    Configuration Management Database.
    '''
    def __init__(conf = ''):
        if not conf:
            conf = os.environ.get('CMDB', "~/.etc/cmdb-conf.json")
        if isinstance(conf, str):
            import jsonpy
            conf = jsonpy.load_file(conf)
        DAL.__init__(self, conf.get('db', 'sqlite://CMDB.sqlite'))
        self.C = conf

        # Building table:
        self.define_table\
            ('building',
             Field('name', length=64,required=True,unique=True),
             Field('abbr', length=8,
                   comment='Building name abbreviation'),
             Field('address', length=128),
             format='%(name)s'
            )
        # Location table:
        self.define_table\
            ('location',
             Field('building', self.building),
             Field('room', length=16),
             primarykey=['building','room'],
             format='%(building)s-%(room)s'
            )

        # VLAN table:
        self.define_table\
            ('vlan',
             Field('name', length=64,required=True,uniqe=True),
             Field('number', 'integer')
            )

        # Device table:
        self.define_table\
            ('device',
             Field('name', length=64,required=True,uniqe=True),
             Field('location', length=64),
             Field('sla', length=64),
             Field('ipv4', self.ipv4)
            )

        # IP address table:
        ##  x   IP <== m:m ==> Device
        ##  x   IP <== m:m ==> MAC
        self.define_table\
            ('ipv4',
             Field('lastseen', 'datetime'),
             Field('via', length=8,requires=IS_IN_SET(conf['IP']['discover'])),
             format='%(city)s, %(state)s')
        self.define_table\
            ('subnet',
             Field('name', length=64,required=True,uniqe=True),
             Field('start', length=4),
             Field('end', length=4),
             Field('vlan', self.vlan),
             Field('doc', 'text')
            )

        # MAC add: MAC <== m:1 ==> Device

        pass
