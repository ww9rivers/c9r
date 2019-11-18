#
# Unit test for c9r.mail.parser
#

from c9r.mail.parser import parse_addr, parse_date, Parser

msg = {
    'date': 'Sat, 22 Mar 2014 08:03:51 -0400',
    'From': 'Wei Wang <weiwang@umich.edu>' }

## Parsing date
def test_1():
    assert parse_date(msg) == 1395489831

## Parsing address
def test_2():
    assert parse_addr(msg, 'From') == 'weiwang@umich.edu'

## Parsing a message
def test_3():
    mtext = "\n".join([
        "Subject: Parser test",
        "Date: Sat, 22 Mar 2014 08:03:50 -0400",
        "From: Wei Wang <weiwang@umich.edu>",
        "To: Wei Wang <weiwang@med.umich.edu>",
        "",
        "This is the content of a test message."])
    parz = Parser()
    em = parz(mtext)
    assert em['to'] == 'weiwang@med.umich.edu'
    assert parse_date(em) == 1395489830
