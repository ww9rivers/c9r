#! /usr/bin/env python3

import re
from time import strftime, strptime
from c9r.net.mac import InvalidMACAddress, MACFormat
from c9r.util.filter import Filter
from c9r.pylog import logger


class AP(Filter):
    '''Process Cisco Prime Infractructure AP Inventory report data for the
    UMHS Enterprise Device Inventory project.
    '''
    # Assuming field/column names in header is case-insensitive, use
    # "Model" and "SerialNumber" out of the source data directly.
    map = {
        "ipAddress": "APIPAddress",
        "commonName": "APName",
        "termID": "APName",
        "association": "ControllerName",
        # "model": "Model",
        # "serialNumber": "SerialNumber",
        }
    assigned_values = {
        "isDhcp":               True,
        "Category":		"Communications Systems and Devices",
        "operatingSystem":	"IOS",
        "equipmentSupportGroup":"MCIT-ISO-Network-Support",
        "manufacturer":		"cisco",
        "assetTag":		"",
        "tier":			"Bronze",
        "containsSensitiveData":False,
        "primaryFunctionType":	"Wi-Fi AP",
        "devicebuilding": 	"site",
        "Ownership":		"MCIT",
        "equipmentOwner":	"ISO",
        }
    def write(self, data):
        '''Normalize given data before writing to the pipe.

        /data/ is expected to be a dictionary-type object, with.
        '''
        val = dict(self.assigned_values)
        emac = apname = None
        try:
            emac = data.get("EthernetMAC")
            if not emac:
                return 0
            val['macAddress'] = MACFormat.none(emac)
            rmac = data.get('BaseRadioMAC')
            if rmac:
                data['BaseRadioMAC'] = MACFormat.none(rmac)
            apname = data.get("APName")
            val.update(parse_apname(apname))
            for kd, ks in self.map.items():
                val[kd] = data[ks]
        except Exception as err:
            logger.error('Error {0} - MAC:{1}, AP:{2}'.format(err, emac, apname))
            if not emac:
                return 0
        data.update(val)
        return Filter.write(self, data)


def parse_apname(apname):
    '''Parse a given AP name to get building and hallway/room names.

    These naming convertions are found in the data so far:

      AP-3
      AP_CVC-1100Z-01A
      AP-MIB-C701B-01A
      AP-Mott-F4750C
      AP-Mott-F7825Z-01A
      AP-UHS-2-F2621-01A
      AP-UHS-2-F2900X-01A
      AP-UHS-F6663-01A
      AP-UHS-F7689A-01A
      AP-KEC-299--03A

    Room/hallway types may be guessed by the ending letter of room name/number:

      0-9       Room
      A         ?
      B         ?
      C         Comm closet
      E         Electrical room
      X         Stairwell
      Z         Hallway

    Returns (equipmentBuilding, equipmentFloor, equipmentRoom, equipmentRoomType)
    '''
    site = floor = room = roomtype = None
    apc = re.split('[-_]', apname or '')
    if apc[0].upper() != 'AP':
        logger.info('Unconventional AP name: {0}'.format(apname))
    else:
        site = apc[1]
        if len(apc) > 4 and apc[3]!='':
            floor = apc[2]
            room = apc[3]
        elif len(apc) > 2:
            room = apc[2]
            floor = room[1] if 'A' <= room[0].upper() < 'Z' else room[0]
        roomtype = {
            'A':        "A",
            "B":        "B",
            "C":         "Comm closet",
            "E":         "Electrical room",
            "X":         "Stairwell",
            "Z":         "Hallway"
            }.get(room[-1].upper(), '') if room else ''
    return dict(
        equipmentBuilding=site,
        equipmentFloor=floor,
        equipmentRoom=room,
        equipmentRoomType=roomtype)


if __name__ == '__main__':
    '''Unit test for this filter module.
    '''
    import doctest
    from c9r import app
    class TestApp(app.Command):
        def __call__(self):
            doctest.testfile('tests/CiscoInventory.test')
    TestApp()()
