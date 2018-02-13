#!/usr/bin/env python3

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


class AnnotatedFile(object):
    '''An object supporting the "iterator" protocol for reading CSV file with annotations.'''
    def readline(self):
        '''Read next line from the file. Empty the line buffer first if it's not.'''
        if self.linebuffer is None:
            return self.file.readline(self)
        line = self.linebuffer
        self.linebuffer = None
        return line

    def peek(self):
        '''Peek into the next line in this file.'''
        if self.linebuffer is None:
            self.linebuffer = self.file.readline(self)
        return self.linebuffer

    def __init__(self, f, mode):
        self.linebuffer = None
        if isinstance(f, str):
            self.file = open(f, (mode if mode else 'r')+'b')
        else:
            self.file = f
            self.close_file = (self.file is not f)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if (not self.close_file):
            return  # do nothing
        # clean up
        exit = getattr(self.file, '__exit__', None)
        if exit is not None:
            return exit(*args, **kwargs)
        exit = getattr(self.file, 'close', None)
        if exit is not None:
            exit()

    def __getattr__(self, attr):
        return getattr(self.file, attr)

    def __iter__(self):
        return iter(self.file)
