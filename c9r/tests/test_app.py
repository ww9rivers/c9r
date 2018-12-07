#!/usr/bin/env python3

from __future__ import print_function
import os, sys
from c9r.app import Command
import c9r.pylog
from c9r.pylog import logger
if 'DEBUG' in os.environ:
    c9r.pylog.set_debug()

def test_app():
    dir = os.path.dirname(__file__) if __file__ else 'tests'
    sys.argv += [ '-c', dir+'/app.json', '-c', 'no-such.json', '-c', '--1' ]
    app = Command()
    logger.debug('app.config() = {0}'.format(repr(app.config())))
    logger.debug(format(sys.argv))
    logger.debug('Testing DEBUG logging')
    logger.debug('Testing DEBUG logging with stdout')
    logger.info('INFO message')
    logger.warn('WARNING message')
    logger.error('ERROR message')
    logger.fatal('FATAL message')
    assert len(logger.handlers) == 1
    assert app.config().__module__ == 'c9r.jsonpy'
    #print(app.config().__module__, file=sys.stderr)
    assert app.config().__class__.__name__ == 'Thingy'
    assert app.config('true') == True
    assert app.config('key') == 'value'
    assert app.config('none') == None
    app.clear_config()
    assert app.config() == None
