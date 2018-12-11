#! /usr/bin/env pytest
'''
Unit tests for ../CiscoPI.py.
'''

import sys
from Ofilter import Ofilter
from c9r.util.filter.CiscoPI import Normalizer, Wired, Wireless, WiredSQL, WirelessSQL, WirelessGuest, WirelessUMHS

xout = Ofilter()


def test_1_1():
    '''Testing v1 CiscoPI.Normalizer
    '''
    with Normalizer(xout) as t11:
        for data in [
                {'MACAddress': '1A-2B-3C:4D-5E-6F', 'User': 'Domain\\nUser', 'LastSessionLength': '1 days 2 hrs 35 min 55 sec'},
                {'MACAddress': '00:18:fe:8a:e0:3c', 'User': 'Domain'+chr(10)+'User', 'LastSessionLength': '3 hrs 47 min 26 sec'}
        ]:
            t11.write(data)
    assert xout.readlines() ==  [''.join([
        '{"MACAddress": "1a2b3c4d5e6f", "User": "Domain/nUser", "LastSessionLength": 95755}',
        '{"MACAddress": "0018fe8ae03c", "User": "Domain/nUser", "LastSessionLength": 13646}'
    ])]

def test_1_2():
    t12 = Normalizer(xout.re_init())
    t12.write({'MACAddress': '0018.fe8a.e03d', 'User': 'Domain/User', 'LastSessionLength': '1 min 2 sec'})
    assert xout.readlines() == ['{"MACAddress": "0018fe8ae03d", "User": "Domain/User", "LastSessionLength": 62}']
    t12.close()

def test_1_3():
    '''Prime 3.1 Unique Clients report changed the "Last Session Length" field: '2 hrs 10 min 2 sec' => '2hrs10min 2sec'
    '''
    with Normalizer(xout.re_init()) as t13:
        for data in [{'MACAddress': '00:00:a1:01:a8:7b', 'User': 'normal-user', 'LastSessionLength': '2hrs10min 2sec'}]:
            t13.write(data)
    assert xout.readlines() == ['{"MACAddress": "0000a101a87b", "User": "normal-user", "LastSessionLength": 7802}']

'''    
Test 2: Test v2 CiscoPI.Wired, CiscoPI.Wireless, and Vendor normalization:
'''
apple_inc = {
    'LastSeen': 'Mon Mar 16 06:58:12 EST 2015',
    'User': 'uniqname',
    'MacAddress': '0c:3e:9f:59:f7:e0',
    'Vendor': "Apple,Inc",
    'IPAddress': '10.21.25.201',
    'DeviceIPAddress': '172.24.128.7',
    'Port': 'umhs-8021x',
    'VLANID': '864',
    'State80211': 'Disassociated',
    'EndpointType': '',
    'LastSessionLength': '2 min 3 sec',
    'APName': 'AP-BSRB-2138-01A',
    'APMACAddress': '001a308cb930',
    'APMapLocation': 'Medical School > BSRB > Floor 2',
    'SSID': 'UMHS-8021X',
    'Profile': 'UMHS-8021X',
    'Protocol': '802.11g',
    'HostName': '',
    'CCX': '',
    'E2E': '',
    'AuthenticationMethod': 'wpa2',
    'GlobalUnique': '',
    'LocalUnique': '',
    'LinkLocal': '',
    'APIPAddress': '10.50.39.78',
    'ConnectionType': 'Lightweight',
    'ConnectedInterface': '',
    'AccessTechnologyType': 'Reserved',
    'ConnectionType': 'Wireless'
}

def test_2_1():
    t21 = Wired(xout.re_init())
    assert apple_inc.get('ConnectionType') != 'Wired'
    assert t21.is_filtered(apple_inc) == True
    assert t21.write(apple_inc) == 0
    t21.close()

def test_2_2():
    t22 = Wireless(xout)
    t22.write(apple_inc)
    assert xout.dump() == {"CCX": "", "AccessTechnologyType": "Reserved", "APMapLocation": "Medical School > BSRB > Floor 2", "GlobalUnique": "", "MacAddress": "0c:3e:9f:59:f7:e0", "Vendor": "Apple", "HostName": "", "VLANID": "864", "EndpointType": "", "ConnectedInterface": "", "E2E": "", "LastSeen": "Mon Mar 16 06:58:12 EST 2015", "State80211": "Disassociated", "APIPAddress": "10.50.39.78", "IPAddress": "10.21.25.201", "User": "uniqname", "APName": "AP-BSRB-2138-01A", "Profile": "UMHS-8021X", "LastSessionLength": 123, "ConnectionType": "Wireless", "LocalUnique": "", "LinkLocal": "", "Protocol": "802.11g", "SSID": "UMHS-8021X", "APMACAddress": "001a308cb930", "AuthenticationMethod": "wpa2", "DeviceIPAddress": "172.24.128.7", "Port": "umhs-8021x"}
    t22.close()

"""
Test 3: CiscoPI.WiredSQL,  CiscoPI.WirelessSQL
"""
multi_ipv6 = {
    "LastSeen": "Mon Mar 16 07:25:00 EST 2015",
    "User": "host/MSL00079.umhs.med.umich.edu",
    "MacAddress": "2477036e0ddc",
    "Vendor": "Intel, Inc.",
    "IPAddress": "10.21.120.221",
    "DeviceIPAddress": "10.50.18.11",
    "Port": "umhs-8021x",
    "VLANID": 3570,
    "State80211": "Associated",
    "EndpointType": "none",
    "LastSessionLength": "3 min 4 sec",
    "APName": "AP-NCRC400-s017-01",
    "APMACAddress": "00270d0b7de0",
    "APMapLocation": "Root Area",
    "SSID": "UMHS-8021X",
    "Profile": "UMHS-8021X",
    "Protocol": "802.11n(5GHz)",
    "HostName": "",
    "CCX": "V4",
    "E2E": "V1",
    "AuthenticationMethod": "wpa2",
    "GlobalUnique": "2601:4:f00:169b:69c5:3e56:502:c9cc, 2601:4:f00:169b:7d69:f2e9:e84d:ce95, 2601:4:f00:169b:fc43:88bb:1b43:fdcd",
    "LocalUnique": "",
    "LinkLocal": "fe80::fc43:88bb:1b43:fdcd",
    "APIPAddress": "10.50.17.143",
    "ConnectionType": "Lightweight",
    "ConnectedInterface": "",
    "AccessTechnologyType": "Reserved",
    "ConnectionType": "Wireless"
}

def test_3_1():
    t31 = WiredSQL(xout)
    assert t31.write(multi_ipv6) == 0
    assert t31.is_filtered(multi_ipv6) == True
    t31.close()

def test_3_2():
    t32 = WirelessSQL(xout)
    t32.write(multi_ipv6)
    assert xout.dump() == {"CCX": "V4", "AccessTechnologyType": "Reserved", "APMapLocation": "Root Area", "GlobalUnique": "2601:4:f00:169b:69c5:3e56:502:c9cc, 2601:4:f00:169b:7d69:f2e9:e84d:ce95, 2601:4:f00:169b:fc43:88bb:1b43:fdcd", "MacAddress": "2477036e0ddc", "Vendor": "Intel Inc", "HostName": "", "VLANID": 3570, "EndpointType": "none", "ConnectedInterface": "", "E2E": "V1", "LastSeen": "Mar 16 2015 07:25:00AM", "State80211": "Associated", "APIPAddress": "10.50.17.143", "IPAddress": "10.21.120.221", "User": "host/MSL00079.umhs.med.umich.edu", "APName": "AP-NCRC400-s017-01", "Profile": "UMHS-8021X", "LastSessionLength": 184, "ConnectionType": "Wireless", "LocalUnique": "", "LinkLocal": "fe80::fc43:88bb:1b43:fdcd", "Protocol": "802.11n(5GHz)", "SSID": "UMHS-8021X", "APMACAddress": "00270d0b7de0", "AuthenticationMethod": "wpa2", "DeviceIPAddress": "10.50.18.11", "Port": "umhs-8021x"}
    t32.close()

"""
Test 4: LastSessionLength is integer
"""
def test_4_1():
    apple_inc["ConnectionType"] = "Wired"
    apple_inc["LastSessionLength"] = 124
    t41 = Wired(xout.re_init())
    t41.write(apple_inc)
    assert xout.dump() == {"CCX": "", "AccessTechnologyType": "Reserved", "APMapLocation": "Medical School > BSRB > Floor 2", "GlobalUnique": "", "MacAddress": "0c:3e:9f:59:f7:e0", "Vendor": "Apple", "HostName": "", "VLANID": "864", "EndpointType": "", "ConnectedInterface": "", "E2E": "", "LastSeen": "Mon Mar 16 06:58:12 EST 2015", "State80211": "Disassociated", "APIPAddress": "10.50.39.78", "IPAddress": "10.21.25.201", "User": "uniqname", "APName": "AP-BSRB-2138-01A", "Profile": "UMHS-8021X", "LastSessionLength": 124, "ConnectionType": "Wired", "LocalUnique": "", "LinkLocal": "", "Protocol": "802.11g", "SSID": "UMHS-8021X", "APMACAddress": "001a308cb930", "AuthenticationMethod": "wpa2", "DeviceIPAddress": "172.24.128.7", "Port": "umhs-8021x"}
    t41.close()

"""
Test 5: Guest vs. UMHS
"""
def test_5_1():
    t51 = WirelessGuest(xout)
    t52 = WirelessUMHS(xout)
    # t51 and t52 should both fiter out "Wired" connections:
    assert t51.is_filtered(apple_inc) == True
    assert t52.is_filtered(apple_inc) == True

def test_5_2():
    t51 = WirelessGuest(xout)
    t52 = WirelessUMHS(xout)
    apple_inc["ConnectionType"] = "Wireless"
    # t51 should fiter out "Wireless" with "UMHS-8021X", t52 should not:
    assert t51.is_filtered(apple_inc) == True
    assert t52.is_filtered(apple_inc) == False

def test_5_3():
    t51 = WirelessGuest(xout)
    t52 = WirelessUMHS(xout)
    apple_inc["SSID"] = "MGuest-UMHS"
    # t51 should not fiter out "Wireless" with "MGuest-UMHS", t52 should:
    assert t51.is_filtered(apple_inc) == False
    assert t52.is_filtered(apple_inc) == True
