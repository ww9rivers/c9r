import io, json
from c9r.util.filter import Filter

class Ofilter(Filter):
    def close(self):
        self.re_init()
    def dump(self):
        self.seek(0)
        obj = json.loads(self._buf.read())
        self.seek(0)
        self._buf.truncate(0)
        return obj
    def readlines(self):
        self.seek(0)
        return self._buf.readlines()
    def re_init(self):
        self.seek(0)
        self.truncate()
        return self
    def seek(self, pos):
        return self._buf.seek(pos)
    def tell(self):
        return self._buf.tell()
    def truncate(self, pos=None):
        return self._buf.truncate(pos)
    def write(self, obj):
        return self._buf.write(json.dumps(obj))
    def close(self):
        pass # Do not close on sys.stdout
    def __init__(self):
        super().__init__(None)
        self._buf = io.StringIO()
