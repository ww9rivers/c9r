#!/usr/bin/env python
#
# $Id: map.py,v 1.2 2014/11/16 03:34:33 weiwang Exp $
#
''' API for reading the NSS Device list data in single-line JSON format.
'''

import json


class jsoList(object):
    '''Reader for JSON list, such as the output from nssdevices.py.
    '''
    def close(self):
        '''Close the JSO list file.
        '''
        close(self.jso)

    def included(self, jso):
        '''Check if a given device has an attribute that makes it excluded.

        /jso/   A JSON object to check against rule sets.

        Exclude the entry if it matches an exclusion rule;
        Include the entry if it matches an inclusion rule; or there is none.
        '''
        for xk, xre in self.exclude.iteritems():
            try:
                xval = jso[xk]
                if (isinstance(xre, list) and xval in xre) or xre.match(xval):
                    logger.debug('Object {0} excluded for {1}:{2}'.format(jso, xk, xval))
                    return False
            except KeyError as xe:
                logger.debug(format(xe))
        for xk, xre in self.include.iteritems():
            try:
                xval = jso[xk]
                if (isinstance(xre, list) and xval in xre) or xre.match(xval):
                    logger.debug('Object {0} included for {1}:{2}'.format(jso, xk, xval))
                    return True
            except KeyError as xe:
                logger.debug(format(xe))
        return len(self.include) == 0

    def next(self):
        '''Return the next included object from given file.
        '''
        for line in self.jso:
            jso = json.loads(line)
            if self.included(jso):
                return jso
        return None

    def open(self):
        '''Open given data file for read.
        '''
        if not self.jso:
            jsof = self.jsofile
            self.jso = open(jsof, 'r') if isinstance(jsof, basestring) else jsof
        return self

    __enter__ = open

    def __exit__(self, type, value, traceback):
        '''Close the JSO list file.
        '''
        self.close()

    def __init__(self, datafile, exclusion, inclusion={}):
        '''Initialize this JSON list reader.

        /datafile/      (Name of) the JSO list data file.
        /exclude/       Rule set to exclude records from data.
        /include/       Rule set to include records from data.

        The /exclude/ rule set takes priority: If an entry is excluded,
        the /include/ rule set is not checked.

        If the /include/ rule set is empty, an entry is included by default.
        Otherwise, it must be explicitly included.
        '''
        self.jso = None
        self.jsofile = datafile
        self.exclude = exclusion
        self.include = inclusion
