#!/usr/bin/env python
"""
$Id: pexssh.py,v 1.2 2014/03/04 20:51:48 weiwang Exp $


This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
"""

from pexpect import *
import getpass, os, re, sys, time
import paramiko as ssh
from c9r.pylog import logger
from c9r.jsonpy import Null


class CSSHError(Exception):
    '''
    Exception that CSSH may throw.
    '''
    pass

class CSSH(spawn):
    '''
    Configured SSH -- An object to execute remote commands, largely copied from pxssh
    in the Python pexpect package, with some *NIX SSH specific stuff removed and made
    more configurable.

    Usage:

        from c9r.net.pexssh import CSSH
        myssh = CSSH('localhost', conf=None, logfile=None)
        myssh('uptime')
        myssh.logout()

    Current implementation follows pxssh, which seems to suggest that logout then login
    to a different host would not work. CSSH does not seem to work either with multiple
    logins.
    '''
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
        self.flush2([self.newline])
        self.sendline()
        self.flush2()
        prompt = self.newline.split(self.before)
        self.prompt = prompt[-1].strip()
        logger.debug("Prompt set to [%s]" % (self.prompt))

    def expect(self, pattern, timeout=None, searchwindowsize=None):
        if timeout is None:
            timeout = getattr(self.C, 'timeout', 10)
        return spawn.expect(self, pattern, timeout=timeout, searchwindowsize=searchwindowsize)

    def flush2(self, pattern=[EOF], timeout=2):
        '''Flush the input to a specified (list of) pattern(s).'''
        pat = pattern+[TIMEOUT]
        ix = self.expect(pat, timeout)
        logger.debug("Flushing to pattern %s = %d" % (format(pat), ix))
        return self.before

    def get_config(self, conf, attr, default=None):
        return conf.get(attr, self.C.get(attr, default))

    def login(self, host, timeout=None):
        conf = getattr(self.C, host, {})
        if isinstance(conf, Null):
            conf = conf.__dict__
        args = self.get_config(conf, 'args', ['-q'])[:]
        user = self.get_config(conf, 'user')
        if user:
            args += [ '-l', user ]
        port = self.get_config(conf, 'port')
        if port:
            args += [ '-p', port ]
        args.append(host)
        logger.debug("CSSH.login: ssh with args: %s" % (format(args)))
        if timeout is None:
            timeout = conf.get('timeout')
        spawn._spawn(self, 'ssh', args=args)
        xi = self.expect([TIMEOUT,
                          '(?i)Are you sure you want to continue connecting',
                          '(?i)password:',
                          self.prompt0], timeout=timeout)
        logger.debug("Remote host displayed:\n%s%s" % (self.before, self.after))
        if xi == 0: # Timeout
            error = "ERROR: SSH could not login. Here is what SSH said:\n%s\n%s" % (self.before, self.after)
            logger.debug(error)
            return None
        if xi == 1: # SSH does not have the public key. Just accept it.
            self.sendline ('yes')
            xi = self.expect([TIMEOUT, '(?i)password:'], timeout=timeout)
            if xi == 0: # Timeout
                error = "ERROR: SSH could not login. Here is what SSH said:\n%s\n%s" % (self.before, self.after)
                logger.debug(error)
                return None
        if xi == 2:
            password = self.get_config(conf, 'password', None)
            if password is None:
                raise CSSHError("No password for user '%s'" % (user))
            self.sendline(password)
        if self.get_config(conf, 'auto_set_prompt', True):
            self.detect_prompt([] if xi == 3 else [self.prompt0])
        logger.debug("Remote host prompt = [%s]" % (self.prompt))

    def logout(self):
        """
        Sends exit to the remote shell. If there are stopped jobs then
        this automatically sends exit twice.
        """
        self.sendline("exit")
        if self.expect([EOF, "(?i)there are stopped jobs"]) == 1:
            self.sendline("exit")
            self.expect(EOF)
        self.close()
        self.pid = None

    def __call__(self, command, echo=None, prompt='', timeout=10):
        '''
        Send the specified (command) to the remote host and wait for (prompt).
        Return what comes before (prompt) as command output.
        '''
        logger.debug("CSSH(): sending command [%s]" % (command))
        self.sendline(command)
        if echo is None:
            echo = command.strip()
        if echo:
            logger.debug("CSSH(): waiting for command echo [%s]" % (echo))
            xi = self.expect([echo, TIMEOUT, EOF], timeout=timeout)
        if prompt is not None:
            if not prompt:
                prompt = self.prompt
            logger.debug("CSSH(): waiting for prompt [%s]" % (prompt))
            xi = self.expect([prompt, TIMEOUT, EOF], timeout=timeout)
            logger.debug("CSSH.expect returned %d" % (xi))
        output = self.before[:-2]
        logger.debug("Remote output = [%s]" % (output))
        return output

    def __init__(self, host='', conf=Null()):
        options = conf.get('options', {})
        if isinstance(options, Null):
            options = options.__dict__
        ## {timeout, maxread, searchwindowsize, logfile, cwd, env}
        logger.debug("CSSH: spawning with option = %s" % (format(options)))
        spawn.__init__(self, None, **options)
        self.C = conf
        prompt0 = conf.get('prompt', '[#$>]')
        self.prompt0 = re.compile(prompt0)
        self.newline = re.compile("[\r\n]+")
        if host:
            self.login(host)
        logger.debug("CSSH: prompt0 = '%s'" % (format(prompt0)))

if __name__ == '__main__':
    import doctest
    if 'DEBUG' in os.environ:
        log.startLogging(sys.stdout)
    doctest.testfile('test-pexssh.txt')
