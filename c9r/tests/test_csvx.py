#! /usr/bin/env pytest
'''
Unit test for the c9r.csvx package.
'''

import csv
from c9r.csvx.dialect import *

def test_1():
    try:
        getattr(csv, 'QUOTE_ALL')
    except Exception as ex:
        assert False

def test_2():
    try:
        Annotated()
        assert False
    except UnnamedDialect:
        assert True
    except Exception as ex:
        assert False
