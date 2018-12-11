#! /usr/bin/env python3

from c9r.util.filter import Filter


class Trim(Filter):
    ''' Filter to trim extra spaces in (before and after) a string.
    '''
    def write(self, data):
        '''Normalize given data before writing to the pipe.

        /data/ is expected to be a dictionary-type object, with.
        '''
        for xk,xv in data.items():
            data[xk] = xv.strip()
        return Filter.write(self, data)


if __name__ == '__main__':
    import doctest
    doctest.testfile('test/Trim.test')
