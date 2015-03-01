#! /usr/bin/env python
#
# $Id: __init__.py,v 1.6 2015/01/07 19:44:25 weiwang Exp $
#

from Queue import Empty, Queue
from c9r.pylog import logger


class Filter(object):
    '''A filter object reads from an input queue and output to another, acting as a filter
    for CSV record processing.

    A filter object may be specifically open()'ed, or used in a "with" statement. But
    that is optional unless it does not have an open() function.
    '''
    def close(self):
        '''To exit this filter thread.

        Try to close the next filter in chain after the thread is done.
        '''
        klass = type(self).__name__
        logger.debug('{0}: closing, que size = {1}'.format(klass, self.que.qsize()))
        self.__call__()
        try_next('close')
        logger.debug('{0}: closed'.format(klass))

    def flush(self):
        '''Write everything to the next filter.
        '''
        while True:
            try:
                self.next_filter.write(self.next())
            finally:
                break

    def join(self):
        if self.que:
            self.que.join()

    def next(self):
        '''Get the next data item off the queue.
        '''
        try:
            return self.que.get()
        except Empty:
            raise(StopIteration())

    def not_open(self):
        '''Returns True if this Filter is not yet open.
        '''
        return self.que is None

    def open(self):
        '''To start a filter thread/greenlet.
        '''
        if self.not_open():
            self.que = Queue()
            logger.debug('{0}: open - Queue created'.format(type(self).__name__))
        return self

    def try_next(self, act, *args, **kwargs):
        '''Perform /act/ on self.input if it exists.
        '''
        joint = self.next_filter
        fact = getattr(self.input, act, None)
        if callable(fact):
            return fact(*args, **kwargs)
        return Empty

    def write(self, data):
        '''Interface for caller to write to this filter.
        Basically, /data/ is put on queue for self in mult-thread mode;
        Or written to the next filter.
        '''
        if self.que:
            self.que.put(data)
        else:
            self.next_filter.write(data)
        self.flush()

    def __call__(self):
        '''Loop through all queued data and write out to the next filter.
        '''
        self.flush()
        self.que.task_done()

    __enter__ = open
    '''To allow this object to be used with "with".'''

    def __exit__(self, type, value, traceback):
        '''To allow this object to be used with "with".'''
        self.close()

    def __init__(self, next_filter):
        '''Initialize this filter.

        The /next_filter/ is an object that has a next() function and a write() function, which
        will be next in a chain of filters for processing data that will be written to this filter.
        It may be optionally already "open". If it has an open() function, it will be called to
        open it. Otherwise, it is assumed to be already open.

        If /mt/ is True, then use Greenlet threading (multi-threading); Otherwise, single thread.
        '''
        self.que = None
        if callable(getattr(next_filter, 'open', None)):
            next_filter = next_filter.open()
        self.next_filter = next_filter
