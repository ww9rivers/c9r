#!/usr/bin/env python
#
# $Id: app.py,v 1.3 2014/03/27 20:38:27 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2012,2013 9Rivers.net. All rights reserved.

Copyright (c) 2012,2013 University of Michigan. All rights reserved.

Redistribution and use in source and binary forms are permitted
provided that this notice is preserved and that due credit is given
to the University of Michigan at Ann Arbor. The name of the University
may not be used to endorse or promote products derived from this
software without specific prior written permission. This software
is provided ``as is'' without express or implied warranty.

#  A command line skeleton with basic command line parameter handleing.
'''

import getopt, json, os, sys
import logging, logging.handlers
from twisted.python import log, logfile
from c9r.jsonpy import Thingy
from c9r.logger import LevelFileLogObserver

class Command:
    """
    Usage:  %s  [options]

    Options:  -h | --help                  Print this help message
              -c | --config=<config-file>  Specify a configuration file.
                                           Default is [%s]
              -d | --debug                 Debug mode.
              -p | --path=<add-path>       Addition to the PYTHONPATH for modules.
              -t | --test-config           Test the configuration only.

    A configuration file is a text file in the JSON format, used to configure this
    application.
    """
    defaults = {}
    def_conf = ''
    short_opt = "hc:dp:t"
    long_opt = ["help", "config=", "debug", "path=", "test-config"]

    def config(self):
        '''
        Get the configuration of this app.
        '''
        return self.CONF

    def log_debug(self, msg):
        log.msg(msg, logLevel=logging.DEBUG)


    def log_error(self, msg):
        log.msg(msg, logLevel=logging.ERROR)

    def log_info(self, msg):
        log.msg(msg, logLevel=logging.INFO)

    def logging(self, logc):
        '''
        Setup logging for this Command object for debugging or information.

        @param  logc    Configuration object for logging.
        '''
        if not logc: return
        name = logc.get('name')
        if name is None: return

        level = getattr(logc, 'level', 'INFO')
        level = getattr(logging, level.upper())
        rotation = logc.get('rotation', 'daily')
        path = logc.get('path', '/var/log')
        mode = logc.get("mode")
        mode = int(mode, 8) if isinstance(mode, str) and mode[0:2].lower() == '0o'\
            else (mode if isinstance(mode, int) else 0o600)
        xf = logfile.DailyLogFile(name, path, defaultMode=mode) if rotation == 'daily'\
            else logfile.LogFile(name, path, rotateLength=rotation*1000,
                                 maxRotatedFiles=100)
        observer = LevelFileLogObserver(xf, level)
        log.addObserver(observer.emit)

    def usage(self, params=0):
        """
        Print the __doc__ string of this app. An app subclassing c9r.app.Command should
        place the usage information under the class.
        """
        if not params:
            params = (sys.argv[0], self.def_conf)
        docstr = self.__doc__
        if docstr:
            docstr = docstr.strip()
        if not docstr:
            docstr = Command.__doc__
        sys.stderr.write("\n"+(docstr % params)+"\n\n")

    def __call__(self):
        assert False, "Application module needs to define __call__()."

    def __init__(self, short_opts=0, long_opts=0):
        '''
        Tests:

        >>> app = Command()
        '''
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], short_opts or self.short_opt, long_opts or self.long_opt)
        except getopt.GetoptError, err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognized"
            self.usage()
            sys.exit(1)

        self.args = args
        conffile = self.def_conf
        if isinstance(conffile, basestring):
            conffile = [conffile]
        self.debug = False
        self.dryrun = False
        for o, a in opts:
            if o in ("-h", "--help"):
                self.usage()
                sys.exit()
            elif o in ("-c", "--config"):
                conffile.append(a)
            elif o in ("-d", "--debug"):
                self.debug = True
                log.startLogging(sys.stdout)
            elif o in ("-p", "--path"):
                sys.path += a.split(':')
            elif o in ('-t', '--test-config'):
                self.dryrun = True
            else:
                self.__opt_handler(o, a)

        conf = self.defaults
        for cfile in conffile:
            try:
                self.log_debug("%s: reading config file '%s'" % (self.__class__,cfile))
                conf = Thingy(cfile, conf)
            except IOError:
                self.log_debug("%s: config file '%s' not found?" % (self.__class__,cfile))
                pass
            except:
                log.err()
                print "%s: Error loading configuration." % (sys.argv[0])
                raise
        if hasattr(self, 'CONF'):
            self.CONF.update(conf)
        else:
            self.CONF = conf
        paths = self.CONF.get('path','')
        for apath in paths.split(':'):
            if os.path.isdir(apath):
                sys.path.append(apath)
        self.logging(self.CONF.get('logging'))

    def __opt_handler(self, opt, val):
        '''
        Default option handler -- an option is considered unhandled if it reaches this point.
        '''
        assert False, "unhandled option: "+opt
        if not (self.args or self.dryrun):
            self.usage()
            sys.exit(2)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
