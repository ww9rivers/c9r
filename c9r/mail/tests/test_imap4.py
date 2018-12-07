#
#       Unit tests for c9r.mail.imap4
#

import os
import os.path as path
from io import StringIO
import email
from email.parser import BytesParser as EmailParser
from c9r.app import Command
from c9r.pylog import logger
from c9r.mail import imap4, parser

## Load proper configuration:
class App(Command):
    xdir = path.dirname(__file__)
    def_conf = [xdir+'/fetch-conf.json']

cmd = App()
xc = cmd.config()
xd3 = None
im = imap4.Mailbox(xc)

## Make sure there is an IMAP server configured, with a port
def test_0():
    assert type(xc.imap.server) == str
    assert type(xc.imap.port) == int

def test_1():
    xres, xdata = im.search(xc.search)
    email_uids = xdata[0].split()
    assert len(email_uids) > 0
    latest_email_uid = email_uids[-1]
    result, data = im.fetch(latest_email_uid)
    assert type(data[0][1]) == bytes

##  This need at least one of the "UMHS Headlines" messages to be read to succeed
def test_2():
    global xd3
    xr2, xd2 = im.search(xc.search2)
    xr3, xd3 = im.search(xc.search3)
    assert xd2 == [b''] or xd3 == [b''] or len(set(xd3[0].split())-set(xd2[0].split())) > 0

## Search is case insensitive
def test_3():
    xr4, xd4 = im.search(xc.search4)
    assert xd4 == xd3

## Search for something not existing
def test_3_5():
    logger.debug('Searching for: "{0}"'.format(xc.nosuchmail))
    assert im.search(xc.nosuchmail) == ('OK', [b''])

## Lync tests:
def test_4():
    lync = xc.lynctest
    assert im.select(lync.folder)[0] == 'OK'
    xrl, xdl = im.search(lync.search)
    assert xrl == 'OK'
    mlist = xdl[0].split()
    assert len(mlist) > 0
    mlast = mlist.pop()
    mo = im.fetch(mlast)
    assert mo[0] == 'OK'
    msgtxt = mo[1][0][1]
    assert msgtxt != b''
    parse = parser.Parser()
    msg = parse(msgtxt)
    xfrom = msg['from']
    assert xfrom != None and xfrom != ""
    assert (xfrom[-14:] == 'everbridge.net') or (xfrom[-14:] == '@med.umich.edu')
    assert im.select()[0] == 'OK'

## Watch "Archive/cron" folder
def test_5():
    cron = xc.cron
    rc, count = im.select(cron.mailbox)
    assert rc == 'OK'
    assert int(count[0]) > 0

## Watch "Archive/wired-clients" folder
def test_6():
    t6 = xc.get('wired-clients')
    assert t6 is not None
    rc6, count6 = im.select(t6.mailbox)
    assert rc6 == 'OK'
    assert int(count6[0]) >= 0
    rc61, ml61 = im.search(t6.search)
    assert rc61 == 'OK'
    assert ml61 == [b''] or len(ml61[0].split()) > 0

## Search for "ironport-reports"
def test_7():
    r70, c70 = im.select('Inbox')
    assert r70 == 'OK'
    assert int(c70[0]) > 0
    t7 = xc.get('ironport-reports')
    assert t7 is not None
    r71, m71 = im.search(t7.search)
    assert r71 == 'OK'
    assert m71 == [b''] or len(m71[0].split()) > 0

## Testing box creation and archive
def test_8():
    t8 = xc.get('archive-test')
    r81, m81 = im.search(t8.search)
    assert r81 == 'OK'
    m81 = m81[0].split()
    assert len(m81) <= 0 or (im.archive(m81[0], t8.archive) == ('OK', [None]))
