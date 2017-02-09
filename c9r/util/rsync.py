#!/usr/bin/python
##	$Id: rsync.py,v 1.2 2015/05/08 19:55:36 weiwang Exp $;
##
##	Script to run hourly cron jobs for the NSSService account.

import os
from subprocess import PIPE, Popen
from c9r.app import Command
from c9r.pylog import logger
from c9r.file.config import Config
import traceback
import re, time
from os import listdir
from os.path import isfile
from c9r.net.http import put


class Rsync(Config):
    '''Configurable wrapper for calling 'rsync'.

    Defining a separate class allows each job the possibility to run
    independent of each other.
    '''
    defaults = {
        'rsync': [ '/usr/bin/rsync', '-auz',
                   '--info=name1,remove'
                   ], # The rsync command.
        'ssh':   'ssh',
        'opt_i': '-i "{identity}"'
        }

    def __call__(self, job):
        '''Use Popen() with Popen.communicate() to run the command and handle
        standard as well as error outputs.
        '''
        cmd = self.config('rsync')
        args = list(cmd) if isinstance(cmd, list) else [cmd]
        src = job.get('source', './')
        dst = job.get('destination', '{user}@{host}:{path}')\
            .format(**{'host': job.get('host', 'localhost'),
                       'path': job.get('path', './'),
                       'user': job.get('user', os.environ['USER'])})
        opt = job.get('options', [])
        #----------------------------------------
        # Build the RSYNC_RSH option:
        idfile = job.get('identity')
        if idfile:
            if not os.access(idfile, os.R_OK):
                raise IOError('File not readable: "{0}"'.format(idfile))
            opt += [ '-e', ' '.join([self.config('ssh'), self.config('opt_i').format(**job)]) ]
        args += opt + [src, dst]
        logger.debug('Running: {0}'.format(' '.join(args)))
        return Popen(args, stdout=PIPE, stderr=PIPE)

    def __init__(self, conf=None):
        Config.__init__(self, initconf=conf)


class RsyncApp(Command):
    '''This app is used to run a number of configured jobs to use "rsync" to
    synchronize files/folders between the local host and remote hosts.

    Configuration:

      jobs              A list of jobs to run.
      rsync             The system rsync command with options. The default
                        is [ "/usr/bin/rsync", "-auvz" ].

    Job configuration:  Each job is configured as a dict with these attributes:

      destination       Destination spec for the rsync command, e.g.
                          user@hostname:path/
                        Further more, a destination may be configured with
                        three parts:

        host            Hostname part of the destination;
        path            Path to folder name part of the destination;
        user            User id to use on the destination host.

      identity          An SSH identity (key) file name; When an identity file
                        is specified, the "-e" option is added to the rsync
                        command line: [ "-e", "ssh -i {identity}" ] 

      options           An optional list of rsync command line options; 
      source            Source file or folder. Mandatory;

    A sample configuration file:

      {
        "rsync":	[ "/usr/bin/rsync", "-auz", "--info=name1,remove" ],
	"jobs":		[ "job1", "job2" ],

        "job1":	{
		"destination":	"joe@server1.domain.com:./",
		"identity":	"id_Svr1",
		"source":	"./"
	},
        "job2": {
		"source":	"./src/",
		"host":		"server2.domain.com",
		"path":		"./src/",
        }
      }
    '''
    def_conf = '~/.etc/rsync-conf.json'

    def __call__(self):
        '''Run the job as configured and use Popen.communicate() to get outputs,
        assuming that the data is not super large.

        If the return code from the rsync command is not zero (0), then any error

        Returns results for the jobs, each in a dict of dict[status, out, err]
        variable, keyed by job names.
        '''
        rsync = Rsync(self.config())
        results = {}
        for job in self.config('jobs', []):
            run = rsync(self.config(job))
            fout,ferr = run.communicate()
            rc = run.wait()
            logger.debug('Job "{0}":\nReturn code = {1}\n\nOutput: {2}\n\nError: {3}'.format(job, rc, fout, ferr))
            results[job] = dict(status=rc, out=fout.split('\n'), err=ferr)
        return results


def main():
    '''Initiate a NetMap run. Exit if dry-run option is given without running the jobs.

    Must have this main() function for this to be run from another
    python program in a child process.
    '''
    app = RsyncApp()
    if app.dryrun:
        import doctest
        doctest.testfile('test/rsync.text')
    app.exit_dryrun()
    for job, result in app().iteritems():
        logger.info('Result of rsync job "{0}" = {status}, [ {out} ] ({err})'.format(job, **result))

if __name__ == '__main__':
    main()
