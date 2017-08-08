#!/usr/bin/env python
#
# $Id: app.py,v 1.13 2016/06/06 18:15:15 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2012,2013 9Rivers.net. All rights reserved.

#  A command line skeleton with basic command line parameter handleing.
'''

import getopt, json, os, sys
from c9r.jsonpy import Null, Thingy
import logging
import c9r.pylog
from c9r.pylog import logger

if logger is None:
    logger = c9r.pylog.get_logger()


class Command(object):
    """
    Usage:  {0}  [options]

    Options:  -h | --help                  Print this help message
              -c | --config=<config-file>  Specify a configuration file.
                                           Default is {1}
                            --             Clear configuration file list;
                            -<int>         Keep <int> number of config file(s)
                                           in the list: e.g. 2 to keep the first
                                           two; -2 to remove the last two.
                            -<filename>    Remove <filename> from the list.
              -d | --debug                 Debug mode.
              -p | --path=<add-path>       Addition to the PYTHONPATH for modules.
              -t | --test-config           Test the configuration only.
              -v | --verbose               Settting verbose output mode.
{2}
    A configuration file is a text file in the JSON format, used to configure this
    application. Multiple configuration file may be specified; If a configuration
    file name starts with '-', it means to remove that file from the list; If it
    is '--', it means to clear the list.
    """
    defaults = {}
    def_conf = []
    dryrun = False
    short_opt = "hc:dp:tv"
    long_opt = ["help", "config=", "debug", "path=", "test-config", "verbose"]

    def clear_config(self):
        '''Clear configuration in self.CONF to start a clean slate, i.e. in a
        child process running another app.
        '''
        Command.CONF = None

    def config(self, item=None, default=None):
        '''Get the configuration of this app.

        /item/     Optional config item name.
        /default/  Optional default value.

        Returns self.CONF when no item is specified;
        Returns self.CONF[item] if all exists;
        Returns default otherwise.

        Caution: Configuration in this class and all its subclasses are made
        singleton to the c9r.app.Command class. Therefore, it may be necessary
        for a cubclass to assertain about overwriting a configuration item.
        '''
        conf = getattr(self, 'CONF', None)
        if item is None:
            return conf
        if conf is None:
            return default
        return conf.get(item, default)

    def exit_dryrun(self, ecode=0):
        '''Exit with optional /ecode/ if dry-run.
        '''
        if self.dryrun:
            logger.debug("{0}: Dry run. Exiting!".format(self))
            sys.exit(ecode)

    def log_debug(self, msg):
        logger.debug(msg)

    def log_error(self, msg=None):
        if msg is None:
            msg = format(sys.exc_info()[0])
        logger.error(msg)

    def log_info(self, msg):
        logger.info(msg)

    def log_warn(self, msg):
        logger.warn(msg)

    def usage(self, params=None):
        """
        Print the __doc__ string of this app. An app subclassing c9r.app.Command should
        place the usage information under the class.

        If a subclass' __doc__ does not start with "Usage:", the text will be used as
        parameter 2 in forming the usage message.
        """
        global logger
        if params is None:
            params = [sys.argv[0], self.def_conf]
        docstr = self.__doc__
        if docstr:
            docstr = docstr.strip()
        if docstr and docstr.startswith('Usage:'):
            params.append('\n')
        else:
            params.append('\n    '+docstr+"\n" if docstr else '')
            docstr = Command.__doc__
        sys.stderr.write("\n"+docstr.format(*params)+"\n\n")

    def __call__(self):
        assert False, "Application module needs to define __call__()."

    def __init__(self, short_opts=0, long_opts=0):
        '''
        '''
        global logger
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], short_opts or self.short_opt, long_opts or self.long_opt)
        except getopt.GetoptError, err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognized"
            self.usage()
            sys.exit(1)

        if self.config() is None:
            Command.CONF = Thingy(self.defaults)
        self.args = args
        conffile = self.def_conf
        if isinstance(conffile, basestring):
            conffile = list([conffile])
        elif not isinstance(conffile, list):
            conffile = list([])
        self.debug = False
        for o, a in opts:
            if o in ("-h", "--help"):
                self.usage()
                sys.exit()
            elif o in ("-c", "--config"):
                if a[0] == '-':
                    b = a[1:]
                    if b == '-': # Clear conffile list
                        conffile = []
                    else: # Remove one specific conffile entry
                        try:
                            conffile = conffile[:int(b)]
                        except ValueError:
                            conffile = [ x for x in conffile if x != b]
                else:
                    conffile.append(a)
            elif o in ("-d", "--debug"):
                self.debug = True
                c9r.pylog.set_level(logging.DEBUG)
            elif o in ("-p", "--path"):
                sys.path += a.split(':')
            elif o in ('-t', '--test-config'):
                Command.dryrun = True
            elif o in ('-v', '--verbose'):
                self.verbose = True
            else:
                self._opt_handler(o, a)

        conf = self.config()
        for cfile in conffile:
            try:
                logger.debug('reading config file "{0}"'.format(cfile))
                conf = Thingy(os.path.expanduser(cfile), conf)
            except IOError:
                logger.debug("%s: config file '%s' not found?" % (self.__class__, cfile))
            except:
                if self.debug:
                    raise
                sys.exit("Error: %s: Error loading configuration '%s'." % (sys.argv[0], cfile))
        if conf != None and conf != Command.CONF:
            Command.CONF = conf
        paths = self.config('path','')
        for apath in paths.split(':'):
            if os.path.isdir(apath) and not apath in sys.path:
                sys.path.append(apath)
        c9r.pylog.config(conf)

    def _opt_handler(self, opt, val):
        '''
        Default option handler -- an option is considered unhandled if it reaches this point.
        '''
        assert False, "unhandled option: "+opt
        if not (self.args or self.dryrun):
            self.usage()
            sys.exit(2)

if __name__ == '__main__':
    import doctest
    doctest.testfile('tests/app.test')
