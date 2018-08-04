# -*- mode: python; -*-
'''
Tests for c9r.smnp.api.SNMPAPI:
'''

import os,sys
from c9r.file.config import Config
from c9r.snmp.api import SNMPAPI
xc = None
snmp = None
hostname = None


def test_1_config():
    '''
    Test 1: This test file is for doctest.testfile() and it needs a configuration file named
    'test-snmpapi-conf.json' in JSON format.
    '''
    global xc, snmp, hostname
    xc = Config('test-snmpapi-conf.json')
    snmp = SNMPAPI(xc['host'], session=xc['session'])
    hostname = snmp.get('SNMPv2-MIB::sysName', 0)
    assert hostname != None

def test_2_hostname():
    '''
    The hostname should be what's configured:
    '''
    global xc, snmp, hostname
    assert hostname[0] == xc['name']
    name = snmp.get('.1.3.6.1.2.1.1.5', 0)
    assert name[0] == hostname[0]

def test_3_sysname():
    '''
    Getting 'sysName' by its OID should result the same:
    '''
    global xc
    assert snmp.get('.1.3.6.1.2.1.1.5.0')[0] == xc['name']

def test_4_walk1():
    '''
    Walking a scalar value, both ways, should result in a single, matching value:
    '''
    global xc, snmp
    toid = xc['walk1']
    res0 = netsnmp.snmpwalk(toid, Version=xc['session']['Version'], Community=xc['session']['Community'], DestHost=xc['host'])
    res1 = snmp.walk(toid)
    assert res0[0] == res1[0].val
    assert res1[0].val == xc['result1']
    assert type(res1) == "class 'netsnmp.client.VarList'"

def test_5_get_object():
    '''
    Test SNMPAPI.get_object() with prefix removed:
    '''
    global xc, snmp
    assert snmp.get_object('.'.join(['.1.3.6.1.2.1.2.2.1.5', xc['ifindex']]), 'Gauge32') == xc['ifspeed']
    oid_ifspeed = '.'.join(['.1.3.6.1.2.1.2.2.1.5', xc['ifindex']])
    assert snmp.get(oid_ifspeed) == (xc['ifspeed'],)
    assert snmp.get('%s.%s' % ('IF-MIB::ifSpeed', xc['ifindex']))[0] == xc['ifspeed']
    assert int(snmp.get_object('.'.join(['.1.3.6.1.2.1.2.2.1.5', xc['ifindex']]), 'Gauge32')) == int(xc['ifspeed'])

def test_6_walk_object():
    '''
    Test SNMPAPI.walk_object():
    '''
    global xc, snmp
    res3 = snmp.walk_object(xc['walk2'])
    assert res3[xc['case2']] == xc['result2']

def test_7_walk_table():
    '''
    Test SNMPAPI.walk_table():
    '''
    global xc, snmp
    res4 = snmp.walk_table(xc['table'])
    assert res4[xc['case2']][xc['case3']] == xc['result2']
