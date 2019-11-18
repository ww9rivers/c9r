#!/usr/bin/env pytest
'''
Module test for c9r.util.filter.csv.IO/.Reader/.Writer
'''
from c9r.util.jso import Storage

def test_1():
    o = Storage(a=1)
    assert o.a == 1
    assert o['a'] == 1
    o.a = 2
    assert o['a'] == 2
    del o.a
    assert o.a == None
    o['a'] = 3
    assert o['a'] == 3

def test_2_getlist():
    request = Storage()
    request.vars = Storage()
    request.vars.x = 'abc'
    request.vars.y = ['abc', 'def']
    assert request.vars.getlist('x') == ['abc']
    assert request.vars.getlist('y') == ['abc', 'def']
    assert request.vars.getlist('z') == []

def test_3_getfirst():
    request = Storage()
    request.vars = Storage()
    request.vars.x = 'abc'
    request.vars.y = ['abc', 'def']
    assert request.vars.getfirst('x') == 'abc'
    assert request.vars.getfirst('y') == 'abc'
    assert request.vars.getfirst('z') == None

def test_4_getlast():
    request = Storage()
    request.vars = Storage()
    request.vars.x = 'abc'
    request.vars.y = ['abc', 'def']
    assert request.vars.getlast('x') == 'abc'
    assert request.vars.getlast('y') == 'def'
    assert request.vars.getlast('z') == None
