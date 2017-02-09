#!/usr/bin/python


class Service(object):
    '''Service model: Each service has (address, port), where port
    may be the default for a given protocol.

    A service point may be logically composed of a host or a cluster of
    hosts. However, the service must have its own address.
    '''
    def __init__(self, address, protocol, port=None):
        self.address = address
        self.protocol = protocol
        self.port = port or protocol
