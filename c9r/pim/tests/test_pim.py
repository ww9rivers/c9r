'''
Test the (currently) psudo PIM module.
'''

from c9r.pim import PIM

def test_pim():
    pim = PIM()
    assert pim.get('test') == 'changeme'
    assert pim.get('test', 'Y2hhbmdlaXQ=') == 'changeit'
    assert pim.get('test-2') == '247794700:admin:changeme!'
    assert pim.get_account('test') == ['test', 'changeme']
    assert pim.get_account('test-2') == ['admin', 'changeme!']
    assert pim.get_account('test-3') == ['user', 'pass:word']
