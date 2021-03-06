#!/usr/bin/env python3

'''
Unit test for c9r.pylog.
'''

import logging
from c9r import pylog
from c9r.pylog import logger

#
# Test 1: Console logging
#
def test_1():
    pylog.set_debug()
    loggr = pylog.get_logger()
    loggr.debug('This is c9r.pylog DEBUG')
    # No output here. But you should see a DEBUG output.
    loggr.warning('This is c9r.pylog WARNING')
    # No output here. But you should see a WARNING output.

#
# Test 2: The default logger.
#
def test_2():
    logger.info('This is c9r.pylog INFO')
    # No output here. But you should see a WARNING output.

#
# Test 3: Configuring a test logger.
#
def test_3():
    pylog.config({
        'logging': {
            'config': 'test/pylog.conf',
            'name': 'test3'
            }
        }, disable_existing_loggers=False)
    lg3 = pylog.get_logger()
    assert isinstance(lg3, logging.Logger) == True
    assert lg3 != logger
    # What is the logger?

    # This output should be 2, as configured in ./pylog.conf
    assert len(lg3.handlers) == 1

    # This output should be logging.DEBUG, which is 10
    assert lg3.getEffectiveLevel() == 30