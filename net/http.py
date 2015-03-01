#!/usr/bin/env python
'''
$Id$

This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2014 Regents of the University of Michigan.
All rights reserved.

Redistribution and use in source and binary forms are permitted
provided that this notice is preserved and that due credit is given
to the University of Michigan at Ann Arbor. The name of the University
may not be used to endorse or promote products derived from this
software without specific prior written permission. This software
is provided ``as is'' without express or implied warranty.

====

File Uploader
'''

import requests

def put(files, url, data={}):
    '''Upload a give (list of) file(s) to a destination specified by /url/.

    /files/ may be a file name in the form of a string; Or a dict keyed with
    variable and value in filename or binary data object.

    Returns responses from Requests.post() in a dict, keyed by files.
    '''
    if isinstance(files, basestring):
        files = dict(file=files)
    status = dict()
    for var,fdata in files.iteritems():
        parts = { var: (fdata, open(fdata, 'rb') if isinstance(fdata, basestring) else fdata) }
        status[fdata] = requests.post(url, files=parts, data=data)
    return status

def test_main():
    from c9r.app import Command
    cmd = Command()
    print(format(post(self.args[:-1], self.args[-1])))

if __name__ == '__main__':
    test_main()
