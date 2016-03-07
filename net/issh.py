#!/usr/bin/env python

'''Reference: https://gist.github.com/rtomaszewski/3397251
 - example paramiko script with interactive terminal, by Radoslaw Tomaszewski (rtomaszewski)

Modified to work with gevent.
'''

import paramiko as pyssh
import socket
import time
import base64, re, os
from cStringIO import StringIO
from c9r.app import Command
from c9r.file.config import Config
from c9r.pylog import logger
    

class AcceptKeyPolicy(pyssh.client.MissingHostKeyPolicy):
    '''A policy to automatically accept missing host keys, with no warning.
    '''
    def missing_host_key(self, client, hostname, key):
        logger.debug('Accepted missing host key for {0}'.format(hostname))

class EOF(Exception):
    '''End-of-file condition.
    '''

class Error(Exception):
    '''Exception that CSSH may throw.
    '''

class TIMEOUT(Error):
    '''Timeout condition.
    '''

class ExpectedPattern(object):
    '''SSH error with known pattern in message.
    '''
    def search(self, text):
        '''Search for this pattern in given text.
        '''
        return self.regex.search(text)

    def __init__(self, pattern):
        '''Compile the given pattern into regex.
        '''
        self.regex = re.compile(pattern)

class Prompt(ExpectedPattern):
    '''The prompt pattern for PatternList.
    '''
    def __init__(self, prompt):
        '''Initialize this pattern, escape any character that regex uses.
        '''
        for chr in '\\$[]{}().:':
            prompt = ('\\'+chr).join(prompt.split(chr))
        logger.debug("Prompt set to [%s]" % (prompt))
        super(Prompt, self).__init__(prompt)

class PatternList(list):
    '''List of patters for SecureShell.expect().
    '''
    def __init__(self, patterns):
        '''Initiate or copy a list of patterns.
        '''
        self.index_eof = -1
        self.index_timeout = -1
        ix = 0
        for pattern in patterns:
            rex = None
            if pattern is EOF:
                self.index_eof = ix
            elif pattern is TIMEOUT:
                self.index_timeout = ix
            elif isinstance(pattern, ExpectedPattern):
                rex = pattern
            else:
                rex = re.compile(pattern)
            self.append(rex)
            ix += 1


class SecureShell(object):
    '''An interactive SSH client object with configuration.
    '''
    def close(self):
        '''Close the current client connection.
        '''
        self.sshc.close()

    def config(self, item=None, default=None):
        '''Get the configuration of this app.

        /item/     Optional config item name.
        /default/  Optional default value.
        '''
        return self.cfg.config(item, default)

    def connect(self, host, **kwargs):
        profile, params = self.get_credentials(host, **kwargs)
        self.sshc.connect(host, **params)
        logger.debug('Connected to {0} as user "{1}".'.format(host, params.get('username', '<N/A>')))
        self.channel = self.sshc.invoke_shell()
        self.detect_prompt()
        if profile:
            init = profile.get('init')
            if init:
                self.run(init)
                self.flush()

    def detect_prompt(self, prompt0=[]):
        '''This sets the remote prompt to something more unique than # or $.
        This makes it easier for the prompt() method to match the shell prompt
        unambiguously. This method is called automatically by the login()
        method, but you may want to call it manually if you somehow reset the
        shell prompt. For example, if you 'su' to a different user then you
        will need to manually reset the prompt. This sends shell commands to
        the remote host to set the prompt, so this assumes the remote host is
        ready to receive commands.

        Alternatively, you may use your own prompt pattern. Just set the PROMPT
        attribute to a regular expression that matches it. In this case you
        should call login() with auto_prompt_reset=False; then set the PROMPT
        attribute. After that the prompt() method will try to match your prompt
        pattern.

        The idea is copied from 'pxssh' in pexpect.'''
        if prompt0:
            self.flush2(prompt0)
        self.sendline()
        prompt_wait = self.config('prompt_wait', 0.05)
        if prompt_wait:
            time.sleep(prompt_wait)
        self.flush2([self.newline])
        self.sendline()
        if prompt_wait:
            time.sleep(prompt_wait)
        self.flush2()
        self.prompt = Prompt(self.newline.split(self.before)[-1])
        self.flush()

    def do_error(self, msg):
        '''Raise an Error with given message.
        '''
        raise Error(msg)

    def do_exit(self):
        '''Do nothing, exit the current command.
        '''
        pass

    def do_send(self, msg):
        '''Send a given msg to the current connection.
        '''
        return self.sendline(msg)

    def expect(self, patterns, timeout=None):
        '''Read from the channel for any of the specified patterns.

        Returns -1 if none of the patters matches; Or the index
        of the pattern matched.

        Raises EOF or TIMEOUT if any occurred and it is not in the patters.
        '''
        logger.debug("Patterns = {0}".format(patterns))
        self.channel.settimeout(timeout or self.timeout)
        pattern_list = PatternList(patterns)
        try:
            while True:
                buffer = self.channel.recv(9999)
                logger.debug("Recv'ed: {0}".format(buffer))
                if len(buffer) == 0:
                    if pattern_list.index_eof >= 0:
                        return pattern_list.index_eof
                    raise EOF()
                sio = StringIO(buffer)
                # Search for any match of the patterns
                mx = None
                while mx is None:
                    line = sio.readline()
                    if len(line) == 0:
                        break # Go read more from the channel
                    logger.debug("Read line: [%s]" % (line))
                    n = 0
                    for rex in pattern_list:
                        if rex != None:
                            mx = rex.search(line)
                            if mx != None:
                                self.match = mx
                                self.after = sio.read()
                                return -1 if mx is None else n
                        n += 1
                    self.before += line
        except socket.timeout:
            if pattern_list.index_timeout >= 0:
                return pattern_list.index_timeout
            raise TIMEOUT()

    def flush(self):
        '''Flush what is already in cache.
        '''
        self.before = self.after = ''

    def flush2(self, pattern=[EOF], timeout=2):
        '''Flush the input to a specified (list of) pattern(s).'''
        pat = pattern+[TIMEOUT]
        ix = self.expect(pat, timeout)
        logger.debug("Flushing to pattern %s = %d" % (format(pat), ix))
        return self.before

    def get_credentials(self, host, **kwargs):
        '''Get login credentials for the given host.

        General practice in networking is that authentication is ceneralized, allowing
        role (group) and subnet based access control. This function is intended to be
        used as an interface to that mechanism.

        Login credentials may be configured in the app's config file.

        TO-DO: Implement subnet-based credential sets.
        '''
        conf = self.config()
        cat = conf.subnets.get(host, self.default).split('.')
        logger.debug('{0} is device of the "{1}" category'.format(host, cat))
        if len(cat) > 1:
            profile = conf.get('profiles', {}).get(cat[0])
            cat = cat[1]
        params = conf.logins.get(cat) ## Get host subnet specific credentials
        params.update(kwargs)
        try:
            pw = params['password']
            params['password'] = base64.b64decode(pw)
        except:
            # If decoding fails, assume it is already decoded.
            pass
        return profile, params

    def run(self, cmds, expecting=[], host=None, **kwargs):
        '''Connect to specified host, start a shell and run a given 
        set of commands.

        /cmds/ is a list of commands to be executed.

        /expecting/ is a list of expectations in the results.

        /host/ is the name or IP address of a host to connect to.

        /kwargs/ is an optional set of parameters. Any missing
        ones should be configured in the config file.

        Returns result(s) from running the given set of commands in a list of
        tuples, each item is (command, result).
        '''
        if host is not None:
            self.connect(host, **kwargs)
        results = ()
        for cmd in (cmds if isinstance(cmds, list) else [cmds]):
            self.sendline(cmd)
            code = self.wait_for_prompt(expecting)
            logger.debug('Command "{0}" returned {1}.'.format(cmd, code))
            results += (tuple(self.newline.split(self.before, 1)),)
        return results

    def sendline(self, cmd=''):
        '''Send a line to the server.
        '''
        if len(cmd) == 0 or cmd[-1] != '\n':
            cmd += '\n'
        self.channel.send(cmd)
        logger.debug("Sent line: [%s]" % (cmd[:-1]))

    def send_password(self, pw):
        '''Send a password to the server.

        To-Do:
        -- May need device specific password group.
        '''
        try:
            #1. Try the given pw as a key:
            rawpw = self.config(pw)
            #2. If wrong, treat it as Base64 encoded:
            rawpw = base64.b64decode(pw if rawpw is None else rawpw)
        except:
            #3. Else, assume it is clear text:
            rawpw = pw
        self.channel.send(rawpw+'\n')

    def wait_for_prompt(self, expecting=[]):
        '''Wait for the device CLI prompt with a configured delay.
        '''
        prompt_wait = self.config('prompt_wait', 0.05)
        if prompt_wait:
            time.sleep(prompt_wait)
        if expecting is not None:
            return self.expect(expecting+[self.prompt])

    def __init__(self, host=None, **kwargs):
        '''Initialization.

        /host/          Optional hostname. Automatically connects if given.
        /kwargs/        Optional, parameters for connect().
        '''
        super(SecureShell, self).__init__()
        if not hasattr(SecureShell, 'CFG'):
            SecureShell.CFG = Config(
                conf = '~/.ssh/cli-conf.json',
                initconf = {
                    'known_hosts': '~/.ssh/known_hosts',
                    'missing_key': 'add',
                    'prompt_wait': 0.05,
                    }
                )
        self.cfg = Config(initconf=SecureShell.CFG, update=kwargs)
        self.timeout = self.config('timeout', 10)
        self.default = self.config('default', 'default.default')
        logger.debug('Default profile.category = {0}.'.format(self.default))
        self.newline = re.compile(self.config('newline', "[\r\n]+"))
        sshc = pyssh.SSHClient()
        sshc.load_system_host_keys()
        sshc.load_host_keys(os.path.expanduser(self.config('known_hosts')))
        sshc.set_missing_host_key_policy(
            {
                'accept': AcceptKeyPolicy,
                'add': pyssh.client.AutoAddPolicy,
                'warn': pyssh.client.WarningPolicy,
                }.get(self.config('missing_key'), pyssh.client.RejectPolicy)())
        self.sshc = sshc
        self.channel = None
        self.flush()
        if host is not None:
            self.connect(host, **kwargs)

    def _opt_handler(self, o, a):
        '''Ignore any extra command line parameters.'''
        pass

class ISSH(Command):
    '''A configured paramiko-based SSH command line utility for running commands
    on a remote host.

    Arguments:
        0       Name or IP address of a host;
        1+      Command(s) to run on the remote host.

    Also, the SecureShell object in this utility uses "~/.ssh/cli-conf.json" as
    its configuration file to provide login information to different groups of
    devices.
    '''

def main():
    '''Use SecureShell as command runner.
    '''
    cmd = ISSH()
    if cmd.dryrun: # Run unit test
        import doctest
        doctest.testfile('test/issh.txt')
        return
    if not cmd.args:
        return
    host = cmd.args[0]
    logger.debug('Connecting to {0}'.format(host))
    ssh = SecureShell()
    results = ssh.run(host, cmd.args[1:])
    logger.debug('Got {0} result(s)'.format(len(results)))
    for cmd,output in results.iteritems():
        print cmd
        for line in StringIO(output):
            print('\t'+line.rstrip())

if __name__ == '__main__':
    main()
