#!/usr/bin/python
'''
Generic IPv4 subnet

Using CIDR notation, an IPv4 subnet is defined as:

  <dotted.quad.subnet.address>/<bits>

The <bits> portion denotates the number of bits in the subnet mask.

In practice, a subnet is a local network resource, meaning it may be
reused in multiple locations in a large network that are not directly
routed between each other.

It is also often associated with a VLAN.
'''

from pydal import DAL


class Subnet4():
    '''
    '''
    def __init__(self):
        '''Define the "subnet4" table in the CMDB.
        '''
