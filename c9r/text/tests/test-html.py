#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import doctest, os, sys
if 'DEBUG' in os.environ:
    import logging, c9r.pylog
    c9r.pylog.set_level(logging.DEBUG)
from c9r.text.html import Parser

h2t = Parser()

def test_1():
    h2t.feed('<body>')
    h2t.feed('<b><font size="2" face="Arial">Tier:</font><font face="Arial"></font> <font size="2" face="Tahoma">')
    h2t.feed('Platinum</font></b>')
    assert str(h2t.text())=='Tier: Platinum'

def test_2():
    h2t.feed(', Gold')
    assert str(h2t.text())=='Tier: Platinum, Gold'

def test_3():
    h2t.reset().feed('<body>Bronze<br>Incident<p>Text</p><div>Block</div></body>')
    assert h2t.text()=='Bronze\nIncident\nText\nBlock'

def test_4():
    h2t.reset().feed('<body><!-- This is a comment --></body>')
    assert h2t.text()==''

def test_5():
    h2t.reset().feed('<body><!-- This is a')
    h2t.feed('multi-line\\n\\ncomment.')
    h2t.feed('--></body>')
    assert h2t.text()==''

def test_6():
    h2t.reset().feed('<body>This&nbsp;and that</body>')
    assert h2t.text()=='This and that'
    h2t.reset().feed('ASCII v. 中–文')
    assert h2t.text() == 'ASCII v. 中–文'
