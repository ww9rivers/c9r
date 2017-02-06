#! /usr/bin/python
#
# $Id: csvfix.py,v 1.30 2016/06/06 15:36:22 weiwang Exp $
'''
An app to read and print JSON data, in a more readable way.
'''

import sys
from c9r.app import Command
from c9r.pylog import logger
from c9r.util import jso


class App(Command):
    '''Extra Options:
    ==================
      -I | --Indent=4      Number of spaces for JSON indentation.

    '''
    def run(self):
        for arg in self.args or ['-']:
            logger.debug('-- Processing {0}:'.format(arg))
            jso.save_storage(jso.load_storage(sys.stdin if arg=='-' else arg), sys.stdout, self.indent)
        pass

    def __init__(self):
        Command.short_opt += "I:"
        Command.long_opt += ["Indent="]
        self.indent = 4
        Command.__init__(self)

    def _opt_handler(self, opt, val):
        '''
        Default option handler -- an option is considered unhandled if it reaches this point.
        '''
        if opt in ("-I", "--Indent"):
            self.indent = val
        else:
            assert False, "unhandled option: "+opt


if __name__ == '__main__':
    app = App()
    app.run()
