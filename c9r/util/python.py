#!/usr/bin/python
#

import sys

def is_string(xvar):
    '''True if /xvar/ is a string type variable.
    '''
    return isinstance(
        xvar,
        basestring if (not 'major' in sys.version_info) or sys.version_info.major < 3
        else str)

if __name__ == "__main__":
    '''Unit test
    '''
    import doctest
    doctest.testfile('test/python.txt')
