import time
from c9r.pylog import set_debug
from c9r.file.config import Config, TextPassword

cnf = {}
conf3 = {}

def test_1():
    ## Test basics
    global cnf
    cnf = Config(dict(a='aaa', b=time.strftime('%F %H:%M:%S')))
    assert(cnf.config('a') == 'aaa')
    try:
        cnf.save()
        assert(False)
    except AttributeError:
        assert(True)

def test_2():
    fname = 'config.test.json'
    global cnf
    cnf.save(fname)
    bcnf = Config(fname)
    assert(bcnf.config('b') == cnf['b'])

def test_3():
    ## Testing initconf
    global conf3
    initconf = dict(a='aaa', b='bbb')
    conf3 = Config(initconf=initconf)
    assert(conf3.config('a') == 'aaa')

def test_4():
    ## Testing include()
    import os
    global conf3
    os.system('touch /tmp/file1')
    os.system('''echo '{ "a": 123 }' > /tmp/file2.json''')
    conf3.include('/tmp')
    assert(conf3.a == 123)
    assert(conf3.b == 'bbb')
    os.system('rm /tmp/file1 /tmp/file2.json')

def test_5():
    ## Hiding password
    import base64
    pw = TextPassword('password', True)
    assert(pw.cleartext() == 'password')
    assert(str(pw) == 'cGFzc3dvcmQ=')
    pw2 = TextPassword('cGFzc3dvcmQ=')
    assert(pw2.cleartext() == 'password')
    assert(str(pw2) == 'cGFzc3dvcmQ=')
