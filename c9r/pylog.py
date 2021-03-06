#!/usr/bin/env python3
#
# $Id: pylog.py,v 1.7 2015/08/13 21:39:54 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2012,2013 9Rivers.net. All rights reserved.

#  A logging module based on Python's logging.
Reference:
  o  http://pingbacks.wordpress.com/2010/12/21/python-logging-tutorial/
'''

import os, sys
import logging
import logging.config
import logging.handlers as Handlers
from configparser import NoSectionError
import __main__ as main

script_file = getattr(main, '__file__', None)
def_config = {
    'config': '~/.etc/pylog.conf',
    'name': os.path.basename(script_file) if script_file else format(main)
    }
PYLOG = globals().get('PYLOG', None)
def_format = "%(asctime)s %(levelname)s %(module)s.%(funcName)s:%(lineno)d %(message)s"
def_level = 'WARN'
logger = globals().get('logger', None)

def config(conf=None, defaults=None, disable_existing_loggers=True):
    '''Configuring the Python logging system.

    The ultimate default result is a logger with the app's main file basename.

    /conf/      A c9r.Thingy (dict-like) object with config info - only the
                "logging" item is used, however.
                If this config is good, it is remembered.
    See logging.config.fileConfig() for details on other parameters.
    '''
    global logger
    global PYLOG
    conf = conf.get('logging', def_config) if conf else def_config
    if conf is None:
        conf = def_config
    fname = conf.get('config', def_config['config'])
    name = conf.get('name', def_config['name'])
    try:
        logging.config.fileConfig(fname, defaults, disable_existing_loggers)
        PYLOG = dict(config=fname, name=name)
    except Exception as err:
        pass
    logger = get_logger(name)
    logger.propagate = False

def get_logger(name=None):
    '''
    Setup logging for this Command object for debugging or information.
    The idea is to have a configured log file for the application, which
    is rotated by Python, whith configurable format, logging level,
    location (path) and mode.

    @param /name/ is name of a logging facility, which is either configured
    in the 'logging.file' given in a call to config(), or configured in
    PYLOG with the name given here.

    if no name is given, and a logger has already been retrieved previously,
    that will be returned to the caller.
    '''
    global logger
    if name is None:
        if logger != None:
            return logger
        name = def_config['name']
    status = 'exists' # Assuming logger exists.
    logger = logging.getLogger(name)
    # The logger should have been configured by the 'config' file;
    # But if not ...
    if len(logger.handlers) == 0:
        # Setup handler for logger:
        cfg = PYLOG.get(name) if (PYLOG and name) else None
        if cfg is None: # Either 'facility' is not configured, or not given.
            handler = logging.StreamHandler(sys.stdout)
            formatter = def_format
            level = def_level
        else:
            formatter = cfg.get('format', def_format)
            path = cfg.get('path', '/var/log/python/pylog.log')
            copies = cfg.get('copies', 2)
            level = cfg.get('level')
            mode = cfg.get('mode')
            mode = int(mode, 8) if isinstance(mode, str) and mode[0:2].lower() == '0o'\
                else (mode if isinstance(mode, int) else 0o600)
            rotation = cfg.get('rotation', 'daily')
            handler = Handlers.RotatingFileHandler(path, maxBytes=rotation, backupCount=copies)\
                if isinstance(rotation, int) \
                else Handlers.TimedRotatingFileHandler(path,
                                                       when = 'midnight' if rotation == 'daily' else 'h',
                                                       backupCount=copies)
        handler.setFormatter(logging.Formatter(formatter))
        if level != None:
            level = getattr(logging, level.upper(), None)
            if level != None:
                handler.setLevel(level)
        logger.addHandler(handler)
        logger.setLevel(level)
        # Test entry:
        status = 'created, handler leve = {0}'.format(level)
    logger.debug(str(name) + ' logger ' + status)
    return logger

def set_debug():
    '''Set logging level to DEBUG.
    '''
    set_level(logging.DEBUG)

def set_level(level=logging.INFO):
    '''Setting the logger's logging activity to a given level.

    @param /level/ is a logging level, defaulting to INFO.
    '''
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


config()


if __name__ == "__main__":
    import doctest
    doctest.testfile('tests/pylog.text')
