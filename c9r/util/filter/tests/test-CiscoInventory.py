#! /usr/bin/env python3
'''
Unit tests for ../CiscoInventory.py.
'''

from c9r.util.filter.CiscoInventory import AP
from Ofilter import Ofilter

ap1 = {
    "EthernetMAC": "112233445560",
    "APIPAddress": "10.20.30.40",
    "APName":      "AP-MIB-C701B-01A"
}
ap2 = {
    "EthernetMAC": "112233445561",
    "APIPAddress": "10.20.30.41",
    "APName":      "AP-Mott-F4750C"
}
ap3 = {
    "EthernetMAC": "112233445562",
    "APIPAddress": "10.20.30.42",
    "APName":      "AP-Mott-F7825Z-01A"
}
ap4 = {
    "EthernetMAC": "112233445563",
    "APIPAddress": "10.20.30.43",
    "APName":      "AP-UHS-2-F2621-01A"
}
ap5 = {
    "EthernetMAC": "112233445564",
    "APIPAddress": "10.20.30.44",
    "APName":      "AP-UHS-2-F2900X-01A"
}
ap6 = {
    "EthernetMAC": "112233445565",
    "APIPAddress": "10.20.30.45",
    "APName":      "AP-UHS-F6663-01A"
}
ap7 = {
    "EthernetMAC": "112233445566",
    "APIPAddress": "10.20.30.46",
    "APName":      "AP-UHS-F7689A-01A"
}

def test_1():
    '''Filter AP data
    '''
    fo = Ofilter()
    t11 = AP(fo)
    t11.write(ap1)
    assert fo.dump() == {
        'APName': 'AP-MIB-C701B-01A', 'Category': 'Communications Systems and Devices', 'macAddress': '112233445560', 'devicebuilding': 'site',
        'equipmentFloor': '7', 'primaryFunctionType': 'Wi-Fi AP', 'equipmentSupportGroup': 'MCIT-ISO-Network-Support', 'tier': 'Bronze',
        'containsSensitiveData': False, 'manufacturer': 'cisco', 'equipmentRoom': 'C701B', 'assetTag': '', 'equipmentOwner': 'ISO',
        'commonName': 'AP-MIB-C701B-01A', 'equipmentRoomType': 'B', 'equipmentBuilding': 'MIB', 'isDhcp': True,
        'termID': 'AP-MIB-C701B-01A', 'Ownership': 'MCIT', 'EthernetMAC': '112233445560', 'APIPAddress': '10.20.30.40',
        'ipAddress': '10.20.30.40', 'operatingSystem': 'IOS'}

    t11.write(ap2)
    assert fo.dump() == {
        'APName': 'AP-Mott-F4750C', 'Category': 'Communications Systems and Devices', 'macAddress': '112233445561', 'devicebuilding': 'site',
        'equipmentFloor': '4', 'primaryFunctionType': 'Wi-Fi AP', 'equipmentSupportGroup': 'MCIT-ISO-Network-Support',
        'tier': 'Bronze', 'containsSensitiveData': False, 'manufacturer': 'cisco', 'equipmentRoom': 'F4750C',
        'assetTag': '', 'equipmentOwner': 'ISO', 'commonName': 'AP-Mott-F4750C', 'equipmentRoomType': 'Comm closet',
        'equipmentBuilding': 'Mott', 'isDhcp': True, 'termID': 'AP-Mott-F4750C', 'Ownership': 'MCIT', 'EthernetMAC': '112233445561',
        'APIPAddress': '10.20.30.41', 'ipAddress': '10.20.30.41', 'operatingSystem': 'IOS'}

    t11.write(ap3)
    assert fo.dump() == {
        'APName': 'AP-Mott-F7825Z-01A', 'Category': 'Communications Systems and Devices', 'macAddress': '112233445562',
        'devicebuilding': 'site', 'equipmentFloor': '7', 'primaryFunctionType': 'Wi-Fi AP', 'equipmentSupportGroup': 'MCIT-ISO-Network-Support',
        'tier': 'Bronze', 'containsSensitiveData': False, 'manufacturer': 'cisco', 'equipmentRoom': 'F7825Z', 'assetTag': '',
        'equipmentOwner': 'ISO', 'commonName': 'AP-Mott-F7825Z-01A', 'equipmentRoomType': 'Hallway', 'equipmentBuilding': 'Mott',
        'isDhcp': True, 'termID': 'AP-Mott-F7825Z-01A', 'Ownership': 'MCIT', 'EthernetMAC': '112233445562', 'APIPAddress': '10.20.30.42',
        'ipAddress': '10.20.30.42', 'operatingSystem': 'IOS'}

    t11.write(ap4)
    assert fo.dump() == {
        'APName': 'AP-UHS-2-F2621-01A', 'Category': 'Communications Systems and Devices', 'macAddress': '112233445563',
        'devicebuilding': 'site', 'equipmentFloor': '2', 'primaryFunctionType': 'Wi-Fi AP', 'equipmentSupportGroup': 'MCIT-ISO-Network-Support',
        'tier': 'Bronze', 'containsSensitiveData': False, 'manufacturer': 'cisco', 'equipmentRoom': 'F2621', 'assetTag': '', 'equipmentOwner': 'ISO',
        'commonName': 'AP-UHS-2-F2621-01A', 'equipmentRoomType': '', 'equipmentBuilding': 'UHS', 'isDhcp': True, 'termID': 'AP-UHS-2-F2621-01A',
        'Ownership': 'MCIT', 'EthernetMAC': '112233445563', 'APIPAddress': '10.20.30.43', 'ipAddress': '10.20.30.43', 'operatingSystem': 'IOS'}

    t11.write(ap5)
    assert fo.dump() == {
        'APName': 'AP-UHS-2-F2900X-01A', 'Category': 'Communications Systems and Devices', 'macAddress': '112233445564', 'devicebuilding': 'site',
        'equipmentFloor': '2', 'primaryFunctionType': 'Wi-Fi AP', 'equipmentSupportGroup': 'MCIT-ISO-Network-Support', 'tier': 'Bronze',
        'containsSensitiveData': False, 'manufacturer': 'cisco', 'equipmentRoom': 'F2900X', 'assetTag': '', 'equipmentOwner': 'ISO',
        'commonName': 'AP-UHS-2-F2900X-01A', 'equipmentRoomType': 'Stairwell', 'equipmentBuilding': 'UHS', 'isDhcp': True,
        'termID': 'AP-UHS-2-F2900X-01A', 'Ownership': 'MCIT', 'EthernetMAC': '112233445564', 'APIPAddress': '10.20.30.44',
        'ipAddress': '10.20.30.44', 'operatingSystem': 'IOS'}

    t11.write(ap6)
    assert fo.dump() == {
        'APName': 'AP-UHS-F6663-01A', 'Category': 'Communications Systems and Devices', 'macAddress': '112233445565', 'devicebuilding': 'site',
        'equipmentFloor': '6', 'primaryFunctionType': 'Wi-Fi AP', 'equipmentSupportGroup': 'MCIT-ISO-Network-Support', 'tier': 'Bronze',
        'containsSensitiveData': False, 'manufacturer': 'cisco', 'equipmentRoom': 'F6663', 'assetTag': '', 'equipmentOwner': 'ISO',
        'commonName': 'AP-UHS-F6663-01A', 'equipmentRoomType': '', 'equipmentBuilding': 'UHS', 'isDhcp': True,
        'termID': 'AP-UHS-F6663-01A', 'Ownership': 'MCIT', 'EthernetMAC': '112233445565', 'APIPAddress': '10.20.30.45',
        'ipAddress': '10.20.30.45', 'operatingSystem': 'IOS'}

    t11.write(ap7)
    assert fo.dump() == {
        'APName': 'AP-UHS-F7689A-01A', 'Category': 'Communications Systems and Devices', 'macAddress': '112233445566', 'devicebuilding': 'site',
        'equipmentFloor': '7', 'primaryFunctionType': 'Wi-Fi AP', 'equipmentSupportGroup': 'MCIT-ISO-Network-Support', 'tier': 'Bronze',
        'containsSensitiveData': False, 'manufacturer': 'cisco', 'equipmentRoom': 'F7689A', 'assetTag': '', 'equipmentOwner': 'ISO',
        'commonName': 'AP-UHS-F7689A-01A', 'equipmentRoomType': 'A', 'equipmentBuilding': 'UHS', 'isDhcp': True, 'termID': 'AP-UHS-F7689A-01A',
        'Ownership': 'MCIT', 'EthernetMAC': '112233445566', 'APIPAddress': '10.20.30.46', 'ipAddress': '10.20.30.46', 'operatingSystem': 'IOS'}
