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

from gluon.html import *
from jslib import *
import gettext, string
_ = gettext.gettext

__all__ = [ 'Button', 'Dialog', 'ErrorMessage', 'Form', 'Grid', 'Help', 'Input' ]


def ui_button (xid, xlabel = '', xicon = ''):
    """
    Rendor HTML stub for a jQuery button.
    """
    xl = _(xlabel)
    xtitle = _(xlabel if xlabel else xid)
    if xtitle: xtitle = " title='%s'"%xtitle
    if xicon != '': xicon = "<span class='ui-icon ui-button-icon-primary ui-icon-%s'></span>" % xicon
    return "<button id='c9r-button-%s'%s>%s%s</button>" % (xid, xtitle, xicon, xl)

def ui_dialog (xid):
    return "<div id='c9r-dialog-%s'></div>" % xid;

def ui_error_message (xmsg):
    return "<div class='ui-state-error'>"+_(xmsg)+"</div>";

def ui_form_input (attrs):
    if '_ui' in attrs:
        xid = attrs['_id'] if '_id' in attrs else 'c9r-input-'+str(id(self))
        Session({'ui': { 'form': { xid: attrs['_ui'] }}})
        attrs['_id'] = xid
        del attrs['_ui']

def ui_grid(xid, xclear = False, xpager = True):
    """
    Return a jQuery Grid HTML skeleton.

    @param	xid	ID of the grid
    @param	xclear	{both, left, right} to clear HTML block
    @param	xpager	True to include a pager in the grid
    """
    xhtml = (("<br clear='%s' style='margin: 0 0 1em 0;' />" % xclear) if xclear else '')\
        + ("<table id='%s-grid' class='scroll' cellpadding='0' cellspacing='0'></table>" % xid)
    if xpager:
        xhtml += ("<div id='%s-pager' class='scroll' style='text-align:center;'></div>" % xid)
    return xhtml

def ui_help (xid):
    return ui_button(xid+'-help', 'Help')

def ui_inline (xtxt, xid = '', xdisplay = True):
    return '<span' + ('' if xid == '' else (" id='%s'" % xid))\
                + " display='" + (xdisplay if isinstance(xdisplay, str) else
                                  ('inline' if xdisplay else 'none'))\
                + ("'>%s</span>" % xtxt)

def ui_list (xarr, xul = 'ul'):
    if xul != 'ul': xul = 'ol'
    return ("<%s><li>" % xul) + "</li><li>".join(xarr) + ("</li></>" % xul)

def ui_pulldown (xid, xopts, xselect = False):
    xkeyed = isinstance(xopts, dict)
    xhtml = "<select id=''>" % xid
    for xkey in xopts:
        xval = xopts[xkey]
        xhtml += "<option value='%s'>%s</option>" % (xkey if xkeyed else xval, xval)
	return xhtml+'</select>'

def ui_toolbar (xbutton):
    """
    Generate HTML code for a tool bar with jQuery UI buttons.
    """
    xhtml = '';
    for xbtn in xbutton:
        xhtml += (ui_button(xbtn[0], xbtn[1], xbtn[2]) if isinstance(xbtn, list)
                  else ("<span style='padding:%s\px;'></span>" % xbtn if isinstance(xbtn, int)
                        else ("<span style='padding:%s\em;'></span>" % xbtn if isinstance(xbtn, float)
                              else ui_button(xbtn))))
        return xhtml


class Button(DIV):
    tag = 'button'
    def __init__(self, xid, **attr):
        icon = attr.get('icon', xid)
        xt = _(attr.get('text', False))
        xl = string.capwords(xid) if not xt or xt == True else xt
        xid="c9r-button-"+xid
        DIV.__init__(self, _(xl), _id=xid)
        widget = { 'text': True if xt else False, 'id': xid }
        if type(icon) == str:
            widget.update({ 'icons': { 'primary': 'ui-icon-'+icon }})
        elif type(icon) == dict:
            widget.update(icon)
        Session({'ui': { 'button': { xid: widget }}})


class Dialog(DIV):
    def __init__(self, xid):
        DIV.__init__(self, _id="c9r-dialog-"+xid)


class ErrorMessage(DIV):
    def __init__(self, xmsg):
        DIV.__init__(self, _(xmsg), _class='ui-state-error')

class Form(FORM):
    '''
    A form object, using jQuery UI theming and client end code.

    Each form component is an HTML input element, optionally with UI data for setting
    them up for interactive event handling.
    '''
    def __init__(self, *components, **attributes):
        ui_form_input(attributes)
        FORM.__init__(self, *components, **attributes)

class Grid(DIV):
    """
    A jQuery.Grid. The grid data is passed in the object initializer, which is
    passed to the page in JSON data in the c9r namespace.

    Tests:
    >>> grid = Grid('grid', { 'grid' : {}, 'pager': {} })
    >>> grid.xml()
    '<div id="c9r-grid-div-grid"><table cellpadding="0" cellspacing="0" class="scroll" id="c9r-grid-grid"></table><div class="scroll" id="c9r-pager-grid" style="text-align:center;"></div></div>'
    >>> from gluon.globals import Response
    >>> current.response = Response()
    >>> Session().xml()
    '<script type="text/javascript">\nvar c9r = c9r || {};\\n$.extend(c9r, function () {\\n  var public = { _S: {"ui": {"grid": {"grid": {"grid": {}, "pager": {}, "id": "grid"}}}} };\\n  $(document).ready(c9r.ui.init);\\n  return public;\\n}());\\n</script>'
    """
    def setup(self, xid, xgrid):
        Session({'ui': { 'grid': { xid : xgrid }}})

    def __init__(self, xid, xgrid=None, xclear=None):
        """
        Return a jQuery Grid HTML skeleton.

        @param	xid	ID of the grid
        @param	xgrid	Grid data
        @param	xclear	{both, left, right} to clear HTML block
        """
        DIV.__init__(self, _id="c9r-grid-div-"+xid)
        if xclear: self.append(BR(_clear=xclear,_style='margin: 0 0 1em 0;'))
        self.append(TABLE(_id='c9r-grid-'+xid,_class='scroll',_cellpadding='0',_cellspacing='0'))
        if xgrid:
            if 'pager' in xgrid:
                self.append(DIV(_id='c9r-pager-'+xid,_class='scroll',_style='text-align:center;'))
            if not "id" in xgrid: xgrid['id'] = xid
            self.setup(xid, xgrid)

class Help(Button):
    def __init__(self, xid=''):
        if xid: xid += '-'
        Button.__init__(self, xid+'help', _icon='help', _text='Help')

class Input(INPUT):
    def __init__(self, *components, **attrs):
        ui_form_input(attrs)
        INPUT.__init__(self, *components, **attrs)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
