#!/usr/bin/python
#
#       $Id: util.py,v 1.4 2015/06/11 19:16:58 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

import re, os, time
import os.path

timespec_re = re.compile('(\d+\.{0,1}\d*)([a-z]{0,2})')
timespec_unit = { '': 1, 's': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800,
                  'mo': 18144000, 'yr': 220752000 }


def compare(ftime, timespec):
    '''Compare a given time to a timespec.

    The /timespec/ may be provided in various ways: If it is an object as
    generated by time.localtime(), it is compared to that of the specified
    path; If it is an integer, it is converted to (now() - timespec) for the
    comparison -- a negative integer is the number of seconds in the future.

    Or, it may be provided as a string, e.g., '3h' for 3 hours, '10m' for
    10 minutes, etc. Valid units are s, m, h, d, w, mo, yr, for second,
    minute, hour, day, month and year. --- This is to be implemented later.
    '''
    if isinstance(timespec, str):
        mx = timespec_re.match(timespec)
        if mx is None:
            raise ValueError('Invalid time spec')
        try:
            timespec = float(mx.group(1))*timespec_unit[mx.group(2)]
        except KeyError as ex: 
            raise ValueError('Invalid time unit: {0}'.format(ex))
    if isinstance(timespec, float) or isinstance(timespec, int):
        tspec = time.time() - timespec
    elif isinstance(timespec, time.struct_time):
        tspec = time.mktime(timespec)
    else:
        raise ValueError('Invalid time spec')
    return ftime-tspec

def created_before(path, timespec):
    '''Check if a file is created before a specified time.
    '''
    fst = os.stat(path)
    return compare(fst.st_atime, timespec) < 0

def modified_before(path, timespec):
    '''Check if a file is modified before specified time.

    /path/      Name (path) of a file.
    /timespec/  Time stamp to compare. See compare() above.
    '''
    fst = os.stat(path)
    return compare(fst.st_mtime, timespec) < 0

def forge_path(path, mode=0o700):
    '''Change current directory to the given path if possible; Otherwise,
    create folders along the path to get there.

    Ref. http://stackoverflow.com/questions/273192/ -- In case the
    directory exists already, its mode may not be what is requested.
    '''
    pwd = os.getcwd()
    try:
        os.makedirs(path, mode=mode)
    except OSError:
        if not os.path.isdir(path):
            raise
    return pwd

if __name__ == '__main__':
    import doctest
    doctest.testfile('test/util.test')
