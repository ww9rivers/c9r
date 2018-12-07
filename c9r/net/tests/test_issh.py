''' Unit test for c9r.net.issh

This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''
import os, re
from paramiko.ssh_exception import SSHException
from c9r.net.issh import SecureShell as pyssh
from c9r.net.issh import ISSH

myssh = ISSH()


def test_localhost():
    global myssh
    myssh = pyssh('localhost') # Must have keychain in place
    uptime = myssh.run('uptime')
    assert isinstance(uptime, tuple)
    uptime = dict(uptime)['uptime']
    mx = re.search('\s+up\s+(\d+).*,\s+\d+\s+users,\s+load average:\s+', uptime)
    if mx is None:
        mx = re.search('\s+up\s+\d+\s+[day|days|hour|hours|min]\s+(\d+):(\d+)', uptime)
    if mx is None:
        print('Failure: Testing issh to run uptime on localhost')

def test_for_sudo_bash_on_localhost():
    global myssh
    myssh.sendline('sudo bash')
    assert myssh.expect(['\[sudo\] password for \w+: ']) == 0

def test_missing_key_policies():
    ssh_reject = pyssh(known_hosts=None, missing_key='reject')
    unknown = '127.0.0.1'
    try:
        ssh_reject.connect(unknown)
        assert False
    except SSHException:
        assert True
    try:
        ssh_fail = pyssh(known_hosts='~/.ssh/known_hosts-file-does-not-exist')
        assert False
    except IOError:
        assert True
    ssh_accept = pyssh(known_hosts='/dev/null', missing_key='accept')
    ssh_accept.connect(unknown)
    uptime = ssh_accept.run('uptime')
    assert isinstance(uptime, tuple)
