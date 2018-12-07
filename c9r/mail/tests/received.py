#!/usr/bin/python3

from io import StringIO
from email.header import decode_header
from pprint import pprint
from c9r.app import Command
from c9r.jsonpy import Thingy
from c9r.file.config import Config
from c9r.mail.imap4 import Mailbox
from c9r.mail.parser import Parser, parse_header


cmd = Command()
conf = Config(initconf=Thingy(dconf={
            "imap":
                {
                "server":	"email.med.umich.edu",
                "port":	993
                },
            "user": "splunk-admin",
            "search": [
                "HEADER FROM no.reply@pagecopy.net",
                "HEADER Message-ID myairmail.com"
                ]
            }))
mbox = Mailbox(conf)
xres, xuid = mbox.search(conf.search)
print("IMAP.search => type = {0}, data = {1}:{2}".format(xres, len(xuid), xuid))

msgid = xuid[0].split()[0]
res, data = mbox.fetch(msgid)
content = data[0][1]
print("IMAP.fetch => uid = {0}, result = {1}:[\n{2}\n]".format(msgid, xres, content))
parser = Parser()
msg = parser(content)
pprint(msg)
pprint(msg['received'])
