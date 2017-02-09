#!/usr/bin/env python
#
## $Id$
##
## Program to monitor major incident emails and automatically forward them.

from c9r.app import Command
import logging
from twisted.python import log


class LogMonitor(Command):
    """
    Usage:  %s  [options] file-to-monitor ...

    Options:  -h | --help                  Print this help message
              -c | --config=<config-file>  Specify a configuration file.
                                           Default is [%s]
              -d | --debug                 Debug mode.
              -p | --path=<add-path>       Addition to the PYTHONPATH for Notifier
                                           modules.
              -t | --test-config           Test the configuration only.

    A configuration file is a text file in the JSON format, used to configure this
    application.

    Multiple files may be spcified on the command line for monitoring.

    By default, the LogMonitor parses each line in a logfile and takes action based on
    configuration.
    """
    def_conf = 'logmonitor-conf.json'

    def __call__(self):
        for fn in self.args:
            log.msg("LogMonitor: monitoring file '%s'" % (fn), logLevel=logging.DEBUG)
        pass

if __name__ == '__main__':
    import doctest, os, sys
    if 'DEBUG' in os.environ:
        LogMonitor.def_conf = 'logmonitor-conf-test.json'
        log.startLogging(sys.stderr)
    log.msg("%s: Debugging" % (sys.argv[0]), logLevel=logging.DEBUG)
    LogMonitor()()
