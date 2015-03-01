#! /usr/bin/env python
#
# $Id: csvio.py,v 1.5 2015/01/07 19:44:25 weiwang Exp $
#

import csv
from c9r.pylog import logger
from c9r.util.filter import Filter


class Reader(object):
    '''A buffered reader to allow rewinding a line.
    '''
    def next(self):
        '''Return the last line if the input is backed up.
        Otherwise, read the next line from file.
        '''
        if self.read:
            self.line = self.input.next()
        else:
            self.read = True
        if None:
            logger.debug('{0}: Read line {1}'.format(type(self).__name__, self.line))
        return self.line

    def backup(self):
        '''Back up: Next call to next() will reread the last line.
        '''
        if not self.read:
            raise StopIteration('This reader is already backed up')
        self.read = False

    def open(self):
        '''To make this object ready for reading.

        This allows the self.input to be a file or a filter.
        '''
        if isinstance(self.input, basestring): # Assuming a filename
            self.input = open(self.input)
        else:
            self.input = self._do_('open')
        return self

    def _do_(self, act):
        '''Perform /act/ on self.input if it exists.
        '''
        fact = getattr(self.input, act, None)
        if callable(fact):
            return fact()
        return self.input

    def __init__(self, input_file):
        '''Initial this reader with an input, which is requried to have a
        next() function.
        '''
        self.input = input_file
        self.line = None
        self.read = True

    __enter__ = open
    '''To allow this object to be used with "with".'''

    def __exit__(self, type, value, traceback):
        '''To allow this object to be used with "with".'''
        self._do_('close')

    def __iter__(self):
        '''Make self an iterator.'''
        return self


class Writer(Filter):
    '''CSV writer: write data received in CSV format, using a csv.DictWriter
    object, to the next filter.

    A Writer is able to write out a CSV header if provided. But it does ntt to be
    explicitly provided.
    '''

    class Shim(object):
        '''A shim between the csv.DictWriter and this Writer class, to
        provide a way for csv.DictWirter to "write" to the que in this
        Writer.
        '''
        def write(self, data):
            if None:
                logger.debug('{0}: Writing to {1}'.format(type(self).__name__, type(self.writer).__name__))
            self.writer.que.put(data)

        def __init__(self, writer):
            self.writer = writer

    def write(self, data):
        '''Run given /data/ through the csv.DictWriter to convert from
        a dict to a CSV row with its writerow() function.
        '''
        try:
            self.writer.writerow(data)
        except ValueError:
            logger.debug('Get ValueError data={0}'.format(data))
            raise

    def __init__(self, next_filter, header, write_header=True):
        '''The CSV writer that writes data to CSV format with given
        header.

        A csv.DictWriter is used to write out each row received in this writer.
        Extra fields in each row is ignored.
        '''
        Filter.__init__(self, next_filter)
        if write_header and header:
            next_filter.write(','.join(header)+'\n')
            logger.debug('Wrote CSV header: {0}'.format(header))
        self.writer = csv.DictWriter(self.Shim(self), header, extrasaction='ignore')


if __name__ == '__main__':
    import doctest
    doctest.testfile('test/csvio.test')
