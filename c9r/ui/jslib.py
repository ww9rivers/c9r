# coding: utf8
#
# This program is licensed under the GPL v3.0, which is found at the URL below:
#      http://opensource.org/licenses/gpl-3.0.html
#
# Copyright (c) 2011, 9Rivers.net, LLC. All rights reserved.
#
# Redistribution and use in source and binary forms are permitted
# provided that this notice is preserved and that due credit is given
# to the copyright holders listed above. The name of the copyright holders
# may not be used to endorse or promote products derived from this
# software without specific prior written permission. This software
# is provided ``as is'' without express or implied warranty.
#

##      Uncomment to track every source file change:
#from gluon.custom_import import track_changes
#track_changes(True)

from gluon import *

def use(lib, a='js', c='static'):
    libs = lib if type(lib) == list else [lib]
    for js in libs:
        current.response.files.append(URL(a=a,c=c,f=js))

def use_app(lib, a=0, c='static'):
    use(lib, a if a else current.request.application, c)

def use_grid(lang='en'):
    use(['jQuery/jqGrid/i18n/grid.locale-%s.js' % lang,
         'jQuery/jqGrid/jquery.jqGrid.js', 'jQuery/jqGrid/ui.jqgrid.css',
         'c9r/grid.js'])

def use_ui():
    use(['jQuery/ui/jquery-ui.js', 'jQuery/ui/jquery-ui.css', 'c9r/ui.js'])

def rupdate(target, md):
    """
    Recursively updates nested dicts
    """
    for key, val in md.items():
        if type(val) == type({}):
            newTarget = target.setdefault(key,{})
            rupdate(newTarget, val)
        else:
            target[key] = val

class Session(SCRIPT):
    """
    A Python object used in web2py to help with passing JavaScript session data in c9r.session.
    """
    data = {}

    def xml(self):
        (fa, co) = self._xml()
        co = "<%s%s>\nvar c9r = c9r || {};\n"\
            "$.extend(c9r, function () {\n"\
            "  $(document).ready(function() { c9r.ui.init(); });\n"\
            "  return { _S: %s };\n"\
            "}());\n</%s>" % (self.tag, fa if fa else ' type="text/javascript"',
                              current.response.json(Session.data), self.tag)
        Session.data = {}
        return co

    def update(self, md):
        rupdate(Session.data, md)

    def __init__(self, md={}):
        SCRIPT.__init__(self)
        self.update(md)
