#! /usr/bin/env python
#
# $Id: __init__.py,v 1.10 2015/04/01 19:57:17 weiwang Exp $
#

from collections import deque
from c9r.pylog import logger


class Queue(deque):
    '''Simulation of gevent.JoinableQueue.
    '''
    def get(self):
        try:
            return self.popleft()
        except IndexError:
            raise(StopIteration())

    def put(self, data):
        self.append(data)

    def qsize(self):
        return len(self)

    def task_done(self):
        pass


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
        qu = self.que
        logger.debug('{0}: closing, que size = {1}, output count = {2}'.format(klass, None if qu is None else qu.qsize(), self.count))
        self.__call__()
        self.try_next('close')
        logger.debug('{0}: closed, que size = {1}, output count = {2}'.format(klass, None if qu is None else qu.qsize(), self.count))

    def flush(self):
        '''Write everything to the next filter.
        '''
        while True:
            try:
                self.next_filter.write(self.next())
                self.count += 1
            finally:
                break

    def join(self):
        '''Join therads on the que.
        '''
        if self.que != None:
            self.que.join()

    def next(self):
        '''Get the next data item off the queue.
        '''
        if self.que is None:
            raise StopIteration('No queue in this filter.')
        return self.que.get()

    def open(self):
        '''To start a filter thread/greenlet.
        '''
        if not self.is_open:
            self.is_open = True
            if self.que is None:
                self.que = Queue()
                logger.debug('{0}: open - Queue created'.format(type(self).__name__))
        return self

    def try_next(self, act, *args, **kwargs):
        '''Perform /act/ on self.input if it exists.
        '''
        fact = getattr(self.next_filter, act, None)
        if callable(fact):
            return fact(*args, **kwargs)
        return Empty

    def write(self, data):
        '''Interface for caller to write to this filter.
        Basically, /data/ is put on queue for self in mult-thread mode;
        Or written to the next filter.
        '''
        if self.que is None:
            self.next_filter.write(data)
            self.count += 1
        else:
            self.que.put(data)

    def __call__(self):
        '''Loop through all queued data and write out to the next filter.
        '''
        self.flush()
        if self.que:
            self.que.task_done()

    __enter__ = open
    '''To allow this object to be used with "with".'''

    def __exit__(self, type, value, traceback):
        '''To allow this object to be used with "with".'''
        self.close()

    def __init__(self, next_filter, is_open=True, que=None):
        '''Initialize this filter.

        The /next_filter/ is an object that has a next() function and a write() function, which
        will be next in a chain of filters for processing data that will be written to this filter.
        It may be optionally already "open". If it has an open() function, it will be called to
        open it. Otherwise, it is assumed to be already open.

        A True /is_open/ parameters means this filter is open, which will cause this filter to
        not queue data but write to the /next_filter/ directly if the given /que/ is None.
        '''
        self.count = 0
        self.is_open = is_open
        self.que = que
        if callable(getattr(next_filter, 'open', None)):
            next_filter = next_filter.open()
        self.next_filter = next_filter
