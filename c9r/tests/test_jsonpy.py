# Tests for class Null(object):

from c9r.jsonpy import Null, Thingy
from c9r.pylog import logger

nx = Null()
assert nx != None
assert nx.items() == []
assert nx.__repr__() == "<class 'c9r.jsonpy.Null'>({})"
assert nx.__str__() == '{}'

nx.new_attr = 'abcde'
assert nx.new_attr == 'abcde'


# Tests for class Thingy(Null):

xo = Thingy(dict(a='aaa', b='bbb'))
assert xo.a == 'aaa'
assert xo.items() == [('a', 'aaa'), ('b', 'bbb')]

from StringIO import StringIO
x1 = Thingy(StringIO('{ "a" : "A-value", "b" : "B-value" }'))
assert x1.b == 'B-value'
assert isinstance(x1, dict) == False
assert isinstance(x1, object) == True
assert isinstance(x1, Null) == True
