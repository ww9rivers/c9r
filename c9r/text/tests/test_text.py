#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import doctest, os, sys
if 'DEBUG' in os.environ:
    import logging, c9r.pylog
    c9r.pylog.set_level(logging.DEBUG)
from c9r.html.text import Parser
h2t = Parser()
h2t.feed('<body>')
h2t.feed('<b><font size="2" face="Arial">Tier:</font><font face="Arial"></font> <font size="2" face="Tahoma">')
h2t.feed('Platinum</font></b>')
assert str(h2t.text())=='Tier: Platinum'

h2t.feed(', Gold')
assert str(h2t.text())=='Tier: Platinum, Gold'

h2t.reset().feed('<body>Bronze<br>Incident<p>Text</p><div>Block</div></body>')
assert h2t.text()=='Bronze\nIncident\nText\nBlock'

h2t.reset().feed('<body><!-- This is a comment --></body>')
assert h2t.text()==''

h2t.reset().feed('<body><!-- This is a')
h2t.feed('multi-line\\n\\ncomment.')
h2t.feed('--></body>')
assert h2t.text()==''

h2t.reset().feed('<body>This&nbsp;and that</body>')
assert h2t.text()=='This and that'
h2t.reset().feed('ASCII v. 中–文')
assert h2t.text() == 'ASCII v. 中–文'
