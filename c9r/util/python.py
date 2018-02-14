#!/usr/bin/env python3
#

import sys

def is_string(xvar):
    '''True if /xvar/ is a string type variable.
    '''
    return isinstance(
        xvar,
        str if ('major' in sys.version_info and sys.version_info.major > 2)
        else basestring)

if __name__ == "__main__":
    '''Unit test
    '''
    import doctest
    doctest.testfile('tests/python.txt')
