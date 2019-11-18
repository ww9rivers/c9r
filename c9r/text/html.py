#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# $Id: text.py,v 1.4 2016/03/28 15:07:15 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2012,2013 9Rivers.net. All rights reserved.

#  Module that converts HTML to plain text.
#  -- Reference: http://docs.python.org/2/library/htmlparser.html
'''

from html.parser import HTMLParser
from html.entities import name2codepoint
from c9r.pylog import logger


class Parser(HTMLParser):
    '''
    Module that converts HTML to plain text.
    '''
    def add_char(self, c):
        '''Add a character to the text. Convert &nbsp; to regular space for text.'''
        if c == 160:
            c = 32
        self.add_text(chr(c) if c < 128 else ('&#%d;'%(c)))

    def add_text(self, text):
        if self.bodymode:
            self.segments.append(text if isinstance(text, str) else text.decode('utf-8'))

    def reset(self):
        HTMLParser.reset(self)
        self.bodymode = True
        self.segments = []
        return self

    def handle_starttag(self, tag, attrs):
        '''Handles tags that by default are rendered with a line break visually. Non-default CSS
        features are not taken into consideratin.'''
        if tag in ('br', 'div', 'p'):
            self.add_text("\n")
        elif tag == "head":
            self.bodymode = False
        elif tag == 'body':
            self.bodymode = True

    def handle_endtag(self, tag):
        if tag == 'body':
            self.bodymode = False

    def handle_data(self, data):
        self.add_text(data)

    def handle_comment(self, data):
        '''Comments are dropped from text.'''
        pass

    def handle_entityref(self, name):
        self.add_char(name2codepoint[name])

    def handle_charref(self, name):
        if name.startswith('x'):
            c = int(name[1:], 16)
        else:
            c = int(name)
        self.add_char(c)

    def handle_decl(self, data):
        '''SGML declarations are dropped from text.'''
        pass

    def text(self):
        '''Return text parsed from HTML document.'''
        lineno = 0
        for txt in self.segments:
            lineno += 1
            logger.debug("%d: %s"%(lineno, txt))
        return ''.join([str(sx.encode('utf-8', 'xmlcharrefreplace'), 'utf-8') for sx in self.segments])

    def __repr__(self):
        return self.text()

    def __init__(self, init=None):
        '''Initialize the parser with optional initial value.
        '''
        HTMLParser.__init__(self, convert_charrefs=False)
        if init: self.add_data(init)

if __name__ == '__main__':
    import doctest
    doctest.testfile('test/text.test')
