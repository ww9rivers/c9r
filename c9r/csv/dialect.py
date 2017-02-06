#!/usr/bin/env python
#
# $Id$
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
        http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2013 9Rivers.com. All rights reserved.
'''

import csv
import re


class Annotated(csv.Dialect):
    '''A self-registering Python CSV dialect.

    The default annotation markers are Cisco LMS DCR module.
    '''
    name = None
    signature = None
    comment = ';'
    markers = {
        'header':  re.compile('HEADER:\s*(?P<section_header>\S+)'),
        'section': re.compile('Start of section (?P<section_number>\d+) - (?P<section_name>\S+.*\S+)')
        }

    def __init__(self, **fmtparams):
        if self.name is None:
            raise Error("Unnamed CSV dialect")
        csv.register_dialect(self.name, **fmtparams)


class AnnotatedFile(file):
    '''An object supporting the "iterator" protocol for reading CSV file with annotations.'''
    def readline(self):
        '''Read next line from the file. Empty the line buffer first if it's not.'''
        if self.linebuffer is None:
            return file.readline(self)
        line = self.linebuffer
        self.linebuffer = None
        return line

    def peek(self):
        '''Peek into the next line in this file.'''
        if self.linebuffer is None:
            self.linebuffer = file.readline(self)
        return self.linebuffer

    def __init__(self, filename, mode='r'):
        file.__init__(self, filename, (mode if mode else 'r')+'b')
        self.linebuffer = None
