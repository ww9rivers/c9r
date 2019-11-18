#! /usr/bin/env pytest
'''
Unit tests for ../csvio.py.
'''

import csv, io, os, sys
from c9r.util.filter.csvio import Reader, Writer
from Ofilter import Ofilter

if 'DEBUG' in os.environ:
    import c9r.pylog
    c9r.pylog.set_debug()

tdata = io.StringIO(u'''
1A-2B-3C:4D-5E-6F,Domain-nUser,1 days 2 hrs 35 min 55 sec
00:18:fe:8a:e0:3c,"Domain-User",3 hrs 47 min 26 sec
''')
header = [ 'MACAddress','User','LastSessionLength' ]

def test_1():
    '''This test fails, although the output is the same as expected,
        Possibly because of CR-LF issue with CVS writer.
    '''
    with Reader(tdata) as xr:
        xout = Ofilter()
        with Writer(xout, header) as xt:
            for data in csv.DictReader(xr, header):
                try:
                    xt.write(data)
                except ValueError as ex:
                    pass
            xt.write({
                'MACAddress': '11:22:33:44:55:66',
                'User': "plainuser",
                'LastSessionLength': '2 hrs 10 min 01 sec'
            })
        assert xout.tell() > 0
        assert xout.seek(0) == 0
        assert xout.readlines() == [''.join([
            '"MACAddress,User,LastSessionLength\\r\\n"',
            '"1A-2B-3C:4D-5E-6F,Domain-nUser,1 days 2 hrs 35 min 55 sec\\r\\n"',
            '"00:18:fe:8a:e0:3c,Domain-User,3 hrs 47 min 26 sec\\r\\n"',
            '"11:22:33:44:55:66,plainuser,2 hrs 10 min 01 sec\\r\\n"'
        ])]

def test_2():
    '''Close writer that writes header but no data is written.
    '''
    xt = Writer(Ofilter(), header, write_header=True)
    xt.close()
