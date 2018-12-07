#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##      CVS: $Id: parser.py,v 1.6 2015/04/07 20:31:32 weiwang Exp $
##
## Reference: http://www.ianlewis.org/en/parsing-email-attachments-python
##

import re
from io import StringIO
from base64 import b64decode
from email.header import decode_header
from email.parser import Parser as StrParser
from email.parser import BytesParser
from email.utils import mktime_tz, parseaddr, parsedate_tz
from c9r.pylog import logger

def parse_addr(msgobj, addr):
    '''Parse specified address from message header.

    /addr/      Address label, e.g. "From", "CC", etc.
    /msgobj/    Email message object generated by email.parser.Parser.
    Returns address found in message; Or '' if not found.
    '''
    xaddr = msgobj.get(addr)
    if not xaddr:
        return ''
    xaddr = parseaddr(xaddr)
    return xaddr[1]

def parse_attachment(message_part):
    '''Parse an email message part into an attachment object.'''
    content_disposition = message_part.get("Content-Disposition", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition and dispositions[0].lower() == "attachment"):
            file_data = message_part.get_payload(decode=True)
            attachment = StringIO(file_data)
            attachment.content_type = message_part.get_content_type()
            attachment.size = len(file_data)
            attachment.name = message_part.get_filename()
            attachment.create_date = None
            attachment.mod_date = None
            attachment.read_date = None

            for param in dispositions[1:]:
                name,value = param.split("=")
                name = name.lower()

                if name == "filename":
                    attachment.name = value
                elif name == "create-date":
                    attachment.create_date = value
                    attachment.ctime = parse_time(value)
                elif name == "modification-date":
                    attachment.mod_date = value
                    attachment.mtime = parse_time(value)
                elif name == "read-date":
                    attachment.read_date = value
                    attachment.atime = parse_time(value)
            return attachment
    return None

def parse_date(msg):
    '''Parse the msg["date"] generated by a Parser object.

    RFC2822 Internet Message Format, section 3.3. Date and Time Specification:
    https://tools.ietf.org/html/rfc2822#section-3.3
    '''
    if 'mtime' not in msg:
        msg['mtime'] = parse_time(msg['date'])
    return msg['mtime']

def parse_time(rfc822):
    '''Parse an date time string in RFC822 spec:
    http://tools.ietf.org/html/rfc822#section-5
    '''
    return mktime_tz(parsedate_tz(rfc822))

def parse_header(item, msgobj):
    '''
    Parse a specified header item in the given message.
    '''
    if msgobj[item] is None:
        return None

    decodefrag = decode_header(msgobj[item])
    item_fragments = []
    for s, enc in decodefrag:
        if enc:
            s = str(s, enc).encode('utf8','replace')
        item_fragments.append(s)
    return ''.join(item_fragments)


class Parser(object):

    def __call__(self, content):
        '''Parse an email message in "content", which is a string or a text input object.

        /content/       Standard encoded email message content.

        Returns parsed message in a dict of (subject, date, body, html, from, to, attachments).
        '''
        if isinstance(content, bytes):
            msgobj = BytesParser().parsebytes(content)
        else:
            msgobj = StrParser().parse(StringIO(content))
        subject = parse_header('Subject', msgobj)
        date = parse_header('Date', msgobj)
        received = []
        for part in (msgobj.get_all('Received') or []):
            lx = self.re_received.split(part)
            tmp = dict(zip(lx[1::2], [ x.strip() for x in lx[2::2] ]))
            tx = tmp.get(';')
            if tx: tmp['time'] = parse_time(tx)
            received.append(tmp)
        fromaddr = parse_addr(msgobj, 'From')
        if date:
            date = date.replace(',', '')
        logger.debug('Parsing message: Date={0}, Subject={1}'.format(date, subject))
        #-------- Parsing attachments:
        attachments = []
        body = None
        html = None
        for part in msgobj.walk():
            attachment = parse_attachment(part)
            if attachment:
                attachments.append(attachment)
            else: # parse text content
                content_type = part.get_content_type()
                if content_type[0:5] == 'text/':
                    payload = str(part.get_payload(decode=True),
                                  part.get_content_charset() or 'ascii',
                                  'replace').encode('utf8','replace')
                if content_type == "text/plain":
                    if body is None:
                        body = ''
                    body += str(payload)
                elif content_type == "text/html":
                    if html is None:
                        html = ''
                    html += str(payload)
                else:
                    logger.debug('Ignored: Content_type "{0}" in message "{1}" from {2}, Date={3}'.format(content_type, subject, fromaddr, date))
        return {
            'subject' : subject,
            'date' : date,
            'received': received,
            # 'received': sorted(received, key=lambda k: k['time']),
            'body' : body,
            'html' : html,
            'from' : fromaddr,
            'to' : parse_addr(msgobj, 'To'),
            'cc' : parse_addr(msgobj, 'CC'),
            'bcc' : parse_addr(msgobj, 'BCC'),
            'attachments': attachments
            }

    def __init__(self):
        self.re_received = re.compile('(from|by|via|with|id|for|;)')

if __name__ == '__main__':
    Print('Unit test is done with pytest.')
