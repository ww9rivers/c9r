#! /usr/bin/python
#
# $Id: csvfix.py,v 1.27 2015/10/28 21:34:34 weiwang Exp $
"""
| This file is part of the c9r package
| Copyrighted by Wei Wang <ww@9rivers.com>
| License: https://github.com/ww9rivers/c9r/wiki/License

An app for log file compression, allowing configurable delay.
"""

import os
import glob
import time
from c9r.app import Command
from c9r.file.config import Config
from c9r.file.util import forge_path, modified_before
from c9r.pylog import logger


class Filer(Config):
    '''An object that work on a configured list of tasks.
    '''
    defaults = {
        'tasks': {
            '*.log':
                {
                'delete':       True,
                }
            },
        'compressor': {
            'bz2':  'bzip2',
            'gz':   'gzip',
            'xz':   'xz',
            'zip':  'zip'
            },
        'include':      '/app/etc/logfiler.d'
        }
    def __call__(self):
        for key,task in self.tasks.iteritems():
            if task.disabled:
                logger.debug('Task "{0}" is disabled.'.format(key))
                continue
            delay = task.get("zip-delay", "4h")
            logger.debug('To process task "{0} (delay: {1})"...'.format(key, delay))
            patt = task.get('files', key)
            archive = task["archive"]
            now = time.time()
            for fname in glob.glob(patt or '*.log'):
                if not modified_before(fname, delay):
                    logger.debug('\tfile "{0}" is still fresh.'.format(fname))
                    continue
                logger.debug('\tcompressing file "{0}"...'.format(fname))
                if archive is None:
                    system
        pass


class Main(Command):
    '''Extra Options:
    ==================
      -L | --List       List the tasks configured.

    '''
    defaults = {
        'tasks': {
            '*.log':
                {
                'delete':       True,
                }
            },
        'include':      '/app/etc/logfiler.d'
        }
    def_conf = '~/.etc/logfiler-conf.json'

    def __call__(self):
        return Filer(self.config())()

    def __init__(self):
        Command.short_opt += "L"
        Command.long_opt += ["List"]
        self.to_list = False
        Command.__init__(self)
        if self.to_list:
            print('Tasks configured:')
            tasks = self.config('tasks', {})
            for name, task in tasks.iteritems():
                if name.strip():
                    pat = task.get('files')
                    print('\t'+name+('\t'+pat if pat.strip() else ''))
            exit(0)

    def _opt_handler(self, opt, val):
        '''
        Default option handler -- an option is considered unhandled if it reaches this point.
        '''
        if opt in ("-L", "--List"):
            self.to_list = True
        else:
            assert False, "unhandled option: "+opt


def main():
    '''
    '''
    app = Main()
    if app.dryrun and os.access('test/logfiler.txt', os.R_OK):
        logger.debug('Configuration tested OK. Running more module tests.')
        import doctest
        doctest.testfile('test/logfiler.txt')
    else:
        app()
    exit(0)

if __name__ == '__main__':
    main()
