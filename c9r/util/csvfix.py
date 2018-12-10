#! /usr/bin/env python3
#
# $Id: csvfix.py,v 1.30 2016/06/06 15:36:22 weiwang Exp $
"""
| This file is part of the c9r package
| Copyrighted by Wei Wang <ww@9rivers.com>
| License: https://github.com/ww9rivers/c9r/wiki/License

A utility for CSV file fixing / manipulation.
"""

# http://stackoverflow.com/a/12639040/249173
from gevent import monkey; monkey.patch_all()

import atexit, glob, os, re
import csv, time
import gevent
import json
from gevent.pool import Pool
from gevent.queue import Empty, JoinableQueue
from zipfile import ZipFile, BadZipfile
from c9r.app import Command
from c9r.file.util import forge_path
from c9r.pylog import logger
import c9r.util.filter
from c9r.util.filter import Filter, csvio
import subprocess
import sys
import traceback

jobqu = JoinableQueue()  # Queue of jobs (tasks)


class CSVFixer(Command):
    '''Extra Options:
    ==================
      -E | --Enabled-only       Only list enabled tasks.
      -L | --List               List the tasks configured.

    Configuration options:

      dialects      A list of CSV dialects, keyed with textual names.
      path          Working folder for the csvfix tool.
      tasks         A list of tasks in dict, keyed with filename template.

    Each task may be configured with:

      postprocess   What to do about the original data file. The value may be:
        bzip2           Compress the file using bzip2;
        delete          The same as "delete true";
        gzip            Compress using gzip;
        xz              Compress using xz;
        zip             Compress using zip.
      delete        Set to true to delete data files after processing.
      delete-empty  Delete output file if empty. Defaults to True.
      destination   Destination folder for fixed files. Defaults to /cwd/.
      dialect       Spcify a CSV dialect, built-in or registered.
      disabled      Set to true to disable this task.
      end-at        Optional regex for end of input file.
      file-mode     Either "w" (overwrite) or "a" (append). Defaults to "w".
      filters       A list of filters for CSV data manipulations.
      header        CSV data column header for output.
      header-clean  Regex for removing special characters. Defaults to '\\W+'.
      header-fix    Optional dict used to fix the header.
      input-format  Format of input data: "csv" or "json". Defaults to "csv".
      pattern       Optional filename template - This overwrites the pattern in the
                    task key.
      read-header   True, if CSV column header is to be read from first line in data.
                    Defaults to false.
      rename        Optional dict for renaming the output file(s).
      skip-line     Skip a given number of lines.
      skip-pass     Skip pass a pattern.
      skip-till     Skip till a pattern.
      times         Set to true to keep time stamps on files. Defaults to false.
      write-header  True, if CSV column header is to be written to output (first line).
                    Defaults to false.

    The optional "file-mode" is used to process multiple files inside a .zip archive.
    The default is "w", which will write output to each individual file. If this is
    set to "a", however, then all output will be written to a single file with the
    name of the first file in the archive. This is to help handle Cisco Prime
    Infrastructure reports that come in ZIP archive with multiple files, each
    containing up to 15000 records.

    If "read-header" is set to true, or if "header" is not configured, the tool will
    try to read the first line of data as header, which potentially could later be
    used as output header, if "write-header" is set to true.

    If "read-header" is set to true, and a "header" list is configured, then the tool
    will write the output with the configured "header", meaning some columne may be
    re-ordered, removed, or added if any of the filters adds data fields.

    The "header-fix" is a dict indexed by regular expressions used to match column
    titles in the header after it is read, to fix text that may not be suitable as
    header in some situations. For example, the column title "802.11 State" in Cisco
    Prime Infrastructure is converted to "80211State", which may still be unsuitable
    as a field name in Splunk. A generic conversion is to make the name start with a
    letter or underscore. For example:

        "header-fix":   { "([^A-Z_a-z]+)(\\w+)": "{1}{0}" }

    That will break a string not starting with a letter or underscore into 2 parts,
    then re-build a string with the part starting with a letter or underscore first,
    so for example, "80211State" becomes "State80211".

    The "rename" dict functions in a similar way to that of "header-fix".
    For example:

        "rename":	{ "Unique_clients_for_Splunk(.+)": "usertracking{0}" }

    The key string in the dict is a regular expression to match an input file name.
    When a match is found, the "Unique_clients_for_Splunk" part is changed to
    "usertracking". The rest of the file name (matched by ".+") remains intact.

    More than one entries may be configured for "rename". The renaming process
    stops when the first match is found.

    Dialects:
    ====================
    Dialects is a collection of Python CSV dialect configurations, each with a name
    and a set of parameters that the csv.register_dialect() function recognized.

    For example:

        "nix":
        {
                "quoting":		"QUOTE_ALL",
                "lineterminator":	"\\n"
        }

    Will register a CSV dialect that quotes all fields and use UNIX-style newline
    with the name "nix".

    Filter:
    ====================
    A filter is a Python object that takes another filter object as a receiver. A
    filter has a write() function to receive data, allowing multiple filter objects
    to be connected into a series of pipes.
    '''
    defaults = {
        # By default, look at all .zip files in the current folder.
        'tasks': {
            '*.zip':
                {
                'delete':       True,
                'skip-till':    '^Last Seen,'
                }
            }
        }
    def_conf = '/app/miops/etc/csvfix-conf.json'

    def __call__(self):
        '''Go through list of files to monitor and fix them.

        Each configured task is started as "concurrently" in a greenlet.
        '''
        os.chdir(self.config('path', '.'))
        tasks = self.config('tasks', {})
        for pat,cfg in tasks.iteritems():
            jobqu.put((cfg, pat))
        tasks = min(self.config('threads', 10), jobqu.qsize())
        cwd = os.getcwd()
        logger.debug('Spawning {0} task threads, CWD = {1}.'.format(tasks, cwd))
        tasks = [ gevent.spawn(task, cwd) for x in range(0, tasks) ]
        logger.debug('Waiting for {0} task threads to complete.'.format(len(tasks)))
        #jobqu.join()
        gevent.joinall(tasks)

    def __init__(self):
        Command.short_opt += "EL"
        Command.long_opt += ["Enabled-only", "List"]
        self.enabled_only = self.to_list = False
        Command.__init__(self)
        csvio.register_dialects(self.config('dialects'))
        if self.to_list:
            print('Tasks configured:')
            tasks = self.config('tasks', {})
            for pat in sorted(tasks.keys()):
                if not pat.strip(): continue
                tsk = tasks[pat]
                disabled = tsk.get('disabled', False)
                if disabled and self.enabled_only: continue
                print('\t{0}:\t{1}'.format(
                        pat, {False:'enabled', True:'disabled'}[disabled]))
            exit(0)


    def _opt_handler(self, opt, val):
        '''
        Default option handler -- an option is considered unhandled if it reaches this point.
        '''
        if opt in ("-E", "--Enabled-only"):
            self.enabled_only = True
        elif opt in ("-L", "--List"):
            self.to_list = True
        else:
            assert False, "unhandled option: "+opt


class InvalidInputFormat(Exception):
    '''Error for invalid input-format configuration.
    '''


class JSOReader(object):
    '''Read from the given in_file and parse each line into a dict as in JSON object.
    '''
    def next(self):
        jsobj = json.loads(self.in_file.next())
        logger.debug(str(jsobj))
        return jsobj

    def __init__(self, in_file, fieldnames=None):
        '''Initiate this reader with input /in_file/. The /fieldnames/ value
        is ignored as field names are read form the JSON object.

        TBD:
        x    May use /fields/ as a translation map?
        '''
        self.in_file = in_file


class Pipeline(object):
    '''A Pipeline is an object that creates a Reader and a Writer, and
    connect them to an optional list of filters.

    The Pipeline object will provide configuration data for the Reader and
    Writer, so appropriate data processing may be performed in them.
    '''
    def_config = {              # Default configuration
        'delimiter': ',',       #: comma
        'quotechar': '"'        #: double-quote
        }

    def __call__(self, fnr, fnw):
        ''' Process given file and generate output.

        /fnr/       (Name of) file to read from.
        /fnw/       (Name of) file to write to.

        The /fnr/ file is read with a default csv.DictReader() as of now, or
        a JSOReader object if explicitly configured so.
        -- May need to revise to allow handling of CSV format variations.

        Returns number of rows (records) processed in the CSV file.
        '''
        # Open files if they are given as file names:
        fin = csvio.Reader(open(fnr, 'rU') if isinstance(fnr, basestring) else fnr, self.ends)
        fout = open(fnw, self.file_mode) if isinstance(fnw, basestring) else fnw
        write_header = self.write_header and (fout.tell() == 0)
        # Skip non-data if so configured:
        skip = dict({'line': 0, 'pass': 0, 'till': 0})
        skip.update(self.skip)
        lineno = 0
        while skip['more']:
            try:
                line = fin.next()
            except StopIteration:
                logger.warn('Unexpected end-of-file when skiping to data in {0}:{1}'.format(fnr, lineno))
                return 0
            if skip['till'] and skip['till'].match(line):
                logger.debug('Skip-till matching line {0}: {1}'.format(lineno+1, line))
                fin.backup()
                break
            lineno += 1
            if (skip['pass'] and skip['pass'].match(line)) or\
               (skip['line'] and skip['line'] <= lineno):
                break
            logger.debug('Skipping line {0}: {1}'.format(lineno, line))
        # If no header is configured, assuming the next line in /fin/ is it:
        # TBD: Make output header different than input header, optionally.
        rheader = None
        header = self.header
        logger.debug('{0}: {1}to output CSV header: {2}'.format(fnw, '' if write_header else 'not ', header))
        if self.read_header or header is None:
            try:
                rheader = [ self.header_clean.sub('', x) for x in fin.next().split(',') ]
            except Exception as ex:
                logger.warn('Unexpected error when reading CSV header in {0}:{1}'.format(fnr, lineno))
                return 0
            lineno += 1
            logger.debug('Read header: {0}'.format(rheader))
            for rex, fmt in self.header_fix:
                nhdr = []
                for col in rheader:
                    mx = rex.match(col)
                    if mx:
                        try:
                            col = fmt.format(*mx.groups())
                        except Exception as ex:
                            logger.warn('Exception fixing "{0}" with "{1}" and groups = {2}'.format(col, fmt, mx.groups()))
                    nhdr.append(col)
                rheader = nhdr
            logger.debug('Header fixed: {0}'.format(rheader))
        #
        # Read through the input file and write out: Read error(s) are logged but ignored.
        #
        lineno = 0
        with csvio.Writer(fout, header or rheader, write_header, self.dialect) as fw:
            # filters: Filters to pass data through. If missing, then straight thru.
            filter1 = fw
            try:
                for fltr in reversed(self.filters):
                    modname, cname = fltr.rsplit('.')
                    mod = __import__('c9r.util.filter.'+modname, fromlist=[cname])
                    klass = getattr(mod, cname)
                    filter1 = klass(filter1).open()
            except ImportError:
                logger.warn('ImportError for filter {0}'.format(fltr))
                raise
            csvreader = self.ireader(fin, fieldnames=(rheader or header))
            while True:
                try:
                    line = csvreader.next()
                    lineno += 1
                    filter1.write(line)
                except StopIteration:
                    break
                except Exception as ex:
                    logger.warn('{2}: {0} (lineno = {1})'.format(ex, lineno, type(ex).__name__))
                    logger.debug('\tline = {0})'.format(line))
                    print('-'*60)
                    traceback.print_exc(file=sys.stdout)
                    print('-'*60)
                    #logger.debug(traceback.format_tb(sys.exc_info()))
            if True:
                logger.debug('Closing filter 1: {0}, lines = {1}, fout size = {2}'.format(type(filter1).__name__, lineno, fout.tell()))
                filter1.close()
        return lineno

    def __init__(self, config={}, cwd='.'):
        '''Initialize this CSV IO.

        /cwd/           Current working directory.
        /config/        Configuration for this object, containing these information:
        destination     Destination folder for fixed files. Defaults to /cwd/.
        skip-line       Skip number of lines in the beginning of the input.
        skip-pass       Skip pass a line matching the skip-pass pattern.
        skip-till       Skip till a line matching the skip-till pattern.
        filters         An optional sequential list of filters.
        '''
        self.dest = config.get('destination', cwd)
        ends = config.get('end-at', False)
        self.ends = re.compile(ends) if ends else ends
        skip = dict(more=False)
        # Skip till/pass a line matching a regex. The matching line is included.
        # 'skip-line' => Number of lines to skip from a CSV file
        for sk in [ 'till', 'pass', 'line' ]:
            skipping = config.get('skip-'+sk, 0) # 0 also means False
            if skipping:
                skip['more'] = True
                skip[sk] = re.compile(skipping) if isinstance(skipping, basestring) else skipping
        self.skip = skip
        self.filters = config.get('filters', [])
        self.header = config.get('header', None)
        self.header_clean = re.compile(config.get('header-clean', '\W+'))
        self.header_fix = [ (re.compile(xk),xv) for xk,xv
                            in config.get('header-fix', {}).iteritems() ]
        self.read_header = config.get('read-header', False)
        self.write_header = config.get('write-header', False)
        self.file_mode = config.get("file-mode", 'w')
        input_format = config.get('input-format', 'csv')
        try:
            self.ireader = {
                'csv':  csv.DictReader,
                'json': JSOReader
                }[input_format]
        except KeyError:
            raise InvalidInputFormat(input_format)
        self.dialect = config.get('dialect', None)


def atexit_delete(filename):
    '''A utility function for threaded jobs started in CSVFixer to delete a given file.

    /filename/    Name of the file to delete.
    '''
    try:
        os.unlink(filename)
    except Exception as ex:
        logger.warn('CSVFixer: Exception "{0}" deleting file "{1}".'.format(ex, filename))

def atexit_process(filename, act):
    '''Post process a file with given /act/.
    '''
    if act == 'delete':
        return atexit_delete(filename)
    if act in set([
        'bzip2',        # Compress the file using bzip2;
        'gzip',         # Compress using gzip;
        'xz',           # Compress using xz;
        'zip'           # Compress using zip.
        ]):
        cmd = (act if isinstance(act, list) else [act])+[filename]
        try:
            subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            logger.error('Error from command {0}\n{1}'.format(cmd, err.output))
        return
    logger.debug('Unknown postprocess action: "{0}" "{1}"'.format(act, filename))

def task(cwd):
    '''Task as a gevent Greenlet that processes one file name pattern.

    /cwd/       Current working directory.
    '''
    while True:
        # config  = A dict containing configuration for the task;
        # pattern = Pattern to match for input file names.
        try:
            config, pattern = jobqu.get(timeout=10)
        except Empty:
            break
        if pattern == '' or config.get('disabled', False):
            logger.debug('CSVFixer: Ignore empty pattern or disabled task')
            continue
        pattern = config.get('pattern', pattern) # 'pattern' may be configured inside task
        dest = config.get('destination', cwd)
        forge_path(dest)
        process = Pipeline(config)
        keep_times = config.get('times', False)
        rename = [ (re.compile(xk),xv) for xk,xv in config.get('rename', {}).iteritems() ]
        logger.debug('CSVFixer: task = %s, destination = "%s"' % (pattern, dest))
        for zipfn in glob.glob(pattern):
            stinfo = os.stat(zipfn)
            logger.debug('CSVFixer: Fixing file "{0}", mtime = {1}'.format(
                    zipfn, time.strftime('%c', time.localtime(stinfo.st_mtime))))
            if zipfn[-4:] != '.zip':
                ## Assume that it is a text CSV file if file name does not end with .zip:
                zipf = None
                ziplist = [zipfn]
            else:
                try:
                    zipf = ZipFile(zipfn)
                    ziplist = zipf.namelist()
                    logger.debug('CSVFixer: Found list in zip file = %s' % (format(ziplist)))
                except BadZipfile:
                    logger.warn('CSVFixer: zip file "%s" is bad.' % (zipfn))
                    continue
            fwpath = ''
            for fn in ziplist:
                if fwpath == '' or config.get('file-mode') != 'a':
                    fwname = fn
                    for rex, fmt in rename:
                        mx = rex.search(fwname)
                        if mx:
                            try:
                                fwname = fmt.format(*mx.groups())
                            except Exception as ex:
                                logger.warn('Exception fixing "{0}" with "{1}" and groups = {2}'.format(fn, fmt, mx.groups()))
                            break
                    fwpath = os.path.join(dest, os.path.basename(fwname))
                logger.debug('Processing file "{0}" to "{1}"'.format(fn, fwname))
                lines = process(open(fn, 'r') if zipf is None else zipf.open(fn, 'r'), fwpath)
                logger.debug('{0} lines processed in file "{1}"'.format(lines, fn))
                # Set fixed file's timestamps if so configured:
                if keep_times:
                    os.utime(fwpath, (stinfo.st_mtime, stinfo.st_mtime))
                    logger.debug('Set file "{0}" atime and mtime to {1}'.format(
                            fwpath, time.strftime('%c', time.localtime(stinfo.st_mtime))))
            # Archive the .zip file if configured so
            if config.get('delete', False):
                logger.debug('File "%s" registered to be deleted' % (zipfn))
                atexit.register(atexit_delete, zipfn)
            else:
                act = config.get('postprocess')
                if act != None:
                    logger.debug('File "%s" registered to be postprocessed with "%s"' % (zipfn, act))
                    atexit.register(atexit_process, zipfn, act)
            # Delete empty file if so configured:
            if fwpath != '' and config.get('delete-empty', True) and os.stat(fwpath).st_size < 1:
                os.unlink(fwpath)
                logger.debug('Deleted empty output file "{0}"'.format(fwpath))
        jobqu.task_done()
        logger.debug('Task "{0}" completed'.format(pattern))

def main():
    '''
    '''
    fixr = CSVFixer()
    if fixr.dryrun and os.access('test/csvfix.txt', os.R_OK):
        fixr.log_debug('Configuration tested OK. Running more module tests.')
        import doctest
        doctest.testfile('test/csvfix.txt')
    else:
        fixr()
    exit(0)

if __name__ == '__main__':
    main()
