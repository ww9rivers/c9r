#!/usr/bin/env python
#
# $Id: logger.py,v 1.2 2016/03/28 15:07:15 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
http://opensource.org/licenses/gpl-3.0.html

Copyright (c) 2012,2013 9Rivers.net. All rights reserved.

#  A twisted.python.log based logging module.
Reference:
  o  http://stackoverflow.com/questions/13748222/twisted-log-level-switch
  o  http://twistedmatrix.com/documents/current/core/howto/logging.html
'''

import logging
from twisted.python import log

class LevelFileLogObserver(log.FileLogObserver):
    '''A LogObserver to filter by logging level for loggers based on
    twisted.python.log.

    The twisted.python.log.FileLogObserver.emit() is overloaded to produce
    log messages. The undocumented feature "system" is used to put out the
    log level for each message.'''
    def emit(self, event):
        level = logging.ERROR if event.get('isError')\
            else event.get('logLevel', logging.INFO)
        if level >= self.logLevel:
            event['system'] = str(level)
            log.FileLogObserver.emit(self, event)

    def __init__(self, f, level=logging.INFO):
        log.FileLogObserver.__init__(self, f)
        self.logLevel = level
