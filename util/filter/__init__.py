#! /usr/bin/env python
#
# $Id: __init__.py,v 1.6 2015/01/07 19:44:25 weiwang Exp $
#

import gevent
from gevent.queue import Empty, JoinableQueue
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
        # self.join()
        joint = self.next_filter
        if callable(getattr(joint, 'close', None)):
            logger.debug('{0}: closing+/-joining next filter = {1}'.format(klass, type(joint).__name__))
            if callable(getattr(joint, 'join', None)):
                joint.join()
            if None:
                joint.close()
        logger.debug('{0}: closed'.format(klass))

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
        return self.que != None and self.greent is None

    def open(self):
        '''To start a filter thread/greenlet.
        '''
        if self.not_open():
            self.greent = gevent.spawn(self)
            logger.debug('{0}: greenlet spawned -> {1}'.format(type(self).__name__, type(self.next_filter).__name__))
        return self

    def write(self, data):
        '''Interface for caller to write to this filter.
        Basically, /data/ is put on queue for self in mult-thread mode;
        Or written to the next filter.
        '''
        if self.queue:
            self.que.put(data)
        else:
            self.next_filter.write(data)

    def __call__(self):
        '''Loop through all queued data and write out to the next filter.
        '''
        while True:
            try:
                joint = self.next_filter
                data = self.next()
                joint.write(data)
                if None and type(joint).__name__ == 'file':
                    joint.flush()
                    logger.debug('{0}: writing {1} bytes to file: {2}'.format(type(self).__name__, len(data), data))
            finally:
                break
        self.que.task_done()

    __enter__ = open
    '''To allow this object to be used with "with".'''

    def __exit__(self, type, value, traceback):
        '''To allow this object to be used with "with".'''
        self.close()

    def __init__(self, next_filter, mt=False):
        '''Initialize this filter.

        The /next_filter/ is an object that has a next() function and a write() function, which
        will be next in a chain of filters for processing data that will be written to this filter.
        It may be optionally already "open". If it has an open() function, it will be called to
        open it. Otherwise, it is assumed to be already open.

        If /mt/ is True, then use Greenlet threading (multi-threading); Otherwise, single thread.
        '''
        self.greent = None
        self.que = JoinableQueue() if mt else None
        if callable(getattr(next_filter, 'open', None)):
            next_filter = next_filter.open()
        self.next_filter = next_filter
