#! /usr/bin/env pytest
# -*- mode:python; -*-
'''
Module test for c9r.util.filter.csv.IO/.Reader/.Writer -- NOT DONE YET!
'''
import io, os, sys, time
from c9r.pylog import logger
from c9r.util.filter import Filter
from c9r.util.filter.tests.Ofilter import Ofilter
from c9r.util.csvfix import CSVFixer, Pipeline, InvalidInputFormat

filtered = 0
xout = Ofilter()

class NullFilter(object):
    '''
    A filter counts the number of records passed through.
    '''
    def close(self):
        pass
    def tell(self):
        return 'N/A'
    def write(self, data):
        global filtered
        logger.debug(data.strip())
        filtered += 1

def test_1():
    with Filter(xout) as ff:
        ff.write('A line of text.\n')
        ff.write('Another line.\n')
    assert xout.readlines() == [''.join(['"A line of text.\\n"', '"Another line.\\n"'])]

"""
Test 2: PipeLine for usertracking (Cisco PI wired) data:
"""
def test_2():
    global filtered
    pl = Pipeline({
        #'skip-till': '^Last Seen,',
        "filters":   [ "CiscoPI.Normalizer" ]
    })
    null = NullFilter()
    pl('zips/usertracking_20150331_140015_629.csv', null)
    assert filtered > 0

"""
Test 3: PipeLine on wifitracking (Cisco PI wireless) data:
"""
def test_3():
    p2 = Pipeline({
        'skip-till': '^Last Seen,',
        "filters":   [ "cisco.PINormalizer" ],
        'read-header': True,
        'header': [
            'LastSeen', 'MACAddress', 'Vendor', 'IPAddress', 'DeviceIPAddress', 'Port', 'VLANID',
            'State80211', 'Protocol', 'EndpointType', 'User', 'ConnectionType', 'LastSessionLength',
            'ConnectedInterface', 'AccessTechnologyType',
            'APName', 'APIPAddress', 'APMACAddress', 'APMapLocation', 'SSID', 'Profile', 'HostName',
            'CCX', 'E2E', 'AuthenticationMethod', 'GlobalUnique', 'LocalUnique', 'LinkLocal']
    })
    global filtered
    filtered = 0
    datafile = 'zips/wifitracking_20141107_082014_166.csv'
    try:
        p2(datafile, null)
        assert filtered > 0
    except IOError:
        'Make sure you have the data file: {0}'.format(datafile)

"""
Test 4: Test "input-format" configuration
"""
def test_4():
    try:
        p3 = Pipeline({ 'input-format': 'invalid' })
        assert False
    except InvalidInputFormat:
        assert True

    jsodata = io.StringIO('{"a": 123}\n{"a": 45}')
    xout.re_init()
    try:
        p4 = Pipeline({ 'input-format': 'json', 'header': [ 'a' ], 'dialect': 'nix' })
        p4(jsodata, xout)
    except InvalidInputFormat:
        'Failed!'
        # Expecting 3 lines: 123 / 45 / 2 (number of lines)
    assert xout.readlines() == [''.join(["123", "45", 2])]

"""
Test 5: Test "postprocess" feature
"""
def test_5():
    temp = '/tmp/csvfix-test.csv'
    tempz = temp+'.xz'
    if os.path.isfile(tempz):
        os.unlink(tempz)
        with open(temp, 'w') as ftemp:
            ftemp.write('''Put some random lines of
test before the "color,value" line, which
is the real start of the CSV part of this file.

color,value
red,ff0000
green,00ff00
blue,0000ff
'''
            )

def test_6():
    class CSVFixerTest5(CSVFixer):
        def_conf = 'test/csvfix-test.json'
    fix = CSVFixerTest5()
    fix()
    assert True
