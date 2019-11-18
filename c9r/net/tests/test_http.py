#!/usr/bin/env python3
'''
Unit test for c9r.net.http.py
'''

def test_requests_https_verify():
    import requests
    requests.get('https://www.umich.edu', verify='./ssl')

def test_c9r_net_http():
    from c9r.app import Command
    from c9r.net import http
    cmd = Command()
    if len(cmd.args) > 1:
        print(format(http.put(cmd.args[:-1], cmd.args[-1])))
    else:
        print('''HTTP POST test to be implemented.''')
