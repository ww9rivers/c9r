#! /usr/bin/env pytest
'''
Unit tests for ../Trim.py.
'''

from c9r.util.filter.Trim import Trim
from Ofilter import Ofilter

def test_1():
    fo = Ofilter()
    xt = Trim(fo)
    xt.write({ 'a': '   aa a ', 'b': ' bb  bb ' })
    assert fo.tell() > 0
    assert fo.dump() == { 'a': 'aa a', 'b': 'bb  bb' }
