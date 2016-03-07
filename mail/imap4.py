#!/usr/bin/env python
##
## $Id: imap4.py,v 1.7 2015/07/23 16:03:59 weiwang Exp $;
##
## Module to fetch email for further processing with JSON configuration.
##
## References:
##   1.  imaplib ? IMAP4 protocol client
##       http://docs.python.org/2/library/imaplib.html
##   2.  Python ? imaplib IMAP example with Gmail
##       http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
##   3.  INTERNET MESSAGE ACCESS PROTOCOL - VERSION 4rev1
##       http://tools.ietf.org/html/rfc3501#section-6.4.4


import base64, imaplib
from c9r import jsonpy
from c9r.pylog import logger


class Mailbox(imaplib.IMAP4_SSL):
    """
    Fetch email message from iMAP server.
    """
    def archive(self, auid, abox):
        """
        Archive a given message to the configured archive mail box.
        The mail box is created if it does not exist.
        """
        xcopy = self.uid('COPY', auid, abox)
        if xcopy[0] == 'OK':
            mov, data = self.delete(auid)
        elif xcopy[0] == 'NO' and xcopy[1][0][:11] == '[TRYCREATE]':
            xdir = self.create(abox)
            logger.debug("Created mailbox: {0} = {1}".format(abox, xdir))
            if xdir[0] == 'OK':
                xcopy = self.archive(auid, abox)
        return xcopy

    def delete(self, auid):
        '''
        Mark a message specified by (auid) as deleted.
        '''
        return self.uid('STORE', auid, '+FLAGS', '(\Deleted)')

    def fetch(self, auid):
        '''
        Fetch a message using given (auid).
        '''
        return self.uid('fetch', auid, '(RFC822)')

    def search(self, xcriteria):
        '''
        Search for messages with given criteria.
        @param  xsearch 	Search criteria: either a string, or a list of search elements.
        @return xres            Result of the search: OK, NO, or BAD.
                xuid            A space separated list of UIDs if the search is OK.
        '''
        xsearch = xcriteria if isinstance(xcriteria, str) else '('+' '.join(xcriteria)+')'
        logger.debug("imap4.search: %s" % (xsearch))
        xres, xuid = self.uid('search', None, xsearch)
        return xres, xuid

    def __init__(self, dcon):
        imaplib.IMAP4_SSL.__init__(self, dcon.imap.server, dcon.imap.port)
        try:
            pw = base64.b64decode(dcon.password)
        except:
            # If decoding fails, assume it is already decoded.
            pw = dcon.password
        self.login(dcon.user, pw)
        self.select()


if __name__ == '__main__':
    import doctest
    doctest.testfile('test/imap4.text')
