#! /usr/bin/env python
#
# $Id: csvio.py,v 1.13 2015/12/11 15:16:47 weiwang Exp $
#

import csv
import re
from c9r.pylog import logger
from c9r.util.filter import Filter


class Reader(object):
    '''A buffered reader to allow rewinding a line, with optional /ends/.
    '''
    def next(self):
        '''Return the last line if the input is backed up.
        Otherwise, read the next line from file.
        '''
        if self.read:
            self.line = self.input.next()
        else:
            self.read = True
        line = self.line
        if self.ends and self.ends.match(line):
            logger.debug('Ends proessing at: {0})'.format(line))
            raise StopIteration
        return line

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

    def __init__(self, input_file, ends):
        '''Initial this reader with an input, which is requried to have a
        next() function.
        '''
        self.input = input_file
        self.line = None
        self.read = True
        self.ends = re.compile(ends) if ends else ends

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

    parameters:

    /next_filter/       The target for this writer to write to;
    /header/            Header (a list);
    /write_header/      True to write header (Defaults to true);
    /dialect/           CSV dialect, defaults to 'excel'.
    '''

    class Shim(object):
        '''A shim between the csv.DictWriter and this Writer class, to
        provide a way for csv.DictWirter to "write" to the que in this
        Writer.
        '''
        def write(self, data):
            if data[0:8] == 'LastSeen':
                logger.debug('{0}: Queuing {1} to {2}'.format(type(self).__name__, data, type(self.csvw).__name__))
            Filter.write(self.csvw, data)

        def __init__(self, writer):
            self.csvw = writer

    def write(self, data):
        '''Run given /data/ through the csv.DictWriter to convert from
        a dict to a CSV row with its writerow() function.
        '''
        try:
            if self.header != None:
                # TBD: To use csv.DictWriter.writeheader()
                # SuSE has Python 2.6.x, where the function does not exist.
                # self.csvo.writeheader()
                self.next_filter.write(','.join(self.header)+'\r\n')
                self.header = None
                logger.debug('Wrote header to {0}'.format(self.next_filter))
            self.csvo.writerow(data)
            self.flush()
        except Exception as ex:
            logger.debug('Got Exception {1}, data={0}'.format(data, ex))
            raise

    writerow = write
    '''To give csvio.Writer a writerow() so it's may be used in place of csv.DictWriter.'''

    def __init__(self, next_filter, header, write_header=True, dialect=None):
        '''The CSV writer that writes data to CSV format with given
        header.

        A csv.DictWriter is used to write out each row received in this writer.
        Extra fields in each row is ignored.
        '''
        Filter.__init__(self, next_filter)
        self.csvo = csv.DictWriter(self.Shim(self), header, extrasaction='ignore',
                                   dialect=(dialect or 'excel'))
        self.header = header if write_header else None # Header to write
        logger.debug('write_header={0}, header={1}'.format(write_header, header))


def register_dialects(dialects):
    '''Register a list of CSV dialects (dict of dicts).
    '''
    if dialects is None:
        return
    for name, params in dialects.iteritems():
        quoting = params.get('quoting')
        if quoting and not isinstance(quoting, int):
            params['quoting'] = getattr(csv, quoting)
        csv.register_dialect(name, **params)
        logger.debug('CSV dialect "{0}" registered'.format(name))


if __name__ == '__main__':
    import doctest
    doctest.testfile('test/csvio.test')
