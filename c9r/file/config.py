#!/usr/bin/env python3
#
#       $Id: config.py,v 1.7 2015/12/04 14:55:28 weiwang Exp $
'''
This program is licensed under the GPL v3.0, which is found at the URL below:
	http://opensource.org/licenses/gpl-3.0.html
'''

import os
import os.path
from base64 import b64decode, b64encode
from c9r.util import jso
from c9r.pylog import logger


def conf_update(conf, update):
    '''Update /conf/ object with new /update/ information, which may be an
    instance of dict, an object with dict(), or Config.
    '''
    if update != None:
        conf.update(update.dict()
                    if callable(getattr(update, 'dict', None))
                    else (update.config() 
                          if callable(getattr(update, 'config', None))
                          else (update if isinstance(update, dict)
                                else dict(update))))
    return conf


class Config(object):
    '''An object class for configuration using jso.Storage.
    '''
    def_conf = []
    defaults = {}

    def config(self, item=None, default=None):
        '''Get the configuration of this app.

        /item/     Optional config item name.
        /default/  Optional default value.
        '''
        return self[item] or default

    def include(self, path, ext='.json'):
        '''To include a file or files in a folder that ends with given extension.

        /path/      Path to file or directory to include.
        /ext/       Extension to limit files to include.
        '''
        logger.debug("To include: {0}".format(path))
        lx = len(ext)
        for fn in (os.listdir(path) if os.path.isdir(path) else [path]):
            if not fn is path:
                fn = os.path.join(path, fn)
            fn = os.path.expanduser(fn)
            if fn[-lx:] == ext and os.path.isfile(fn):
                logger.debug("Including file: {0}".format(fn))
                self.load(fn)

    def load(self, filename):
        '''Load a given file, if not loaded yet.

        /filename/      Path to file to be loaded.
        '''
        fn = os.path.expanduser(filename)
        if fn in self.loaded:
            logger.debug('Config file "{0}" already loaded.'.format(xf))
        else:
            self.update(jso.load_storage(fn))

    def save(self, saveto=None):
        '''If there is a file to save to, then save the configuration.
        '''
        if saveto is None:
            saveto = self.save_to
        jso.save_storage(self.CONF, saveto)

    def update(self, conf):
        '''Update this config object with new attributes.
        '''
        conf_update(self.CONF, conf)

    def __getitem__(self, item):
        conf = self.CONF
        return conf if item is None or conf is None else conf[item]

    __getattr__ = __getitem__

    def __init__(self, conf=None, initconf=None, update=None):
        '''Initialize this object, loading all configuration.

        The last item in the list(def_conf+conf) is used for saving this obejct.

        /conf/          An optional list of config files, the last of which is used
                        by save() to write to.
        /initconf/      Initial configuration, either a dict or an object with dict().
        /update/        Optional update to initconf and conf file(s).
        '''
        conf = [] if conf is None else list(conf if isinstance(conf, list) else [conf])
        self.CONF = conf_update(jso.Storage(self.defaults), initconf)
        xf = None
        to_include = list()
        self.loaded = set()
        for xf in self.def_conf+conf:
            try:
                if isinstance(xf, str):
                    logger.debug('...loading config {0}'.format(xf))
                    self.load(xf)
                else:
                    self.update(xf)
                more_include = self.config('include')
                if more_include:
                    to_include.append(more_include)
            except IOError as ex:
                logger.debug('Exception {0} loading config {1}'.format(ex, xf))
        for xf in to_include:
            self.include(xf)
        self.save_to = xf if isinstance(xf, str) else None
        self.update(update)


class TextPassword(object):
    '''A Base64 encoded clear text password.
    '''
    def assign(self, value):
        '''Assigning a given value to self.
        '''
        try:
            clear = b64decode(value)
        except TypeError:
            clear = value
        value = b64encode(clear)
        if value != self.value:
            self.value = value
        return clear.decode("utf-8")
    def cleartext(self):
        return self.assign(self.value)
    def __init__(self, val, is_clear=None):
        self.value = val
        if is_clear is None:
            self.assign(val)
        elif is_clear:
            self.value = b64encode(val.encode())
    def __str__(self):
        return self.value.decode()
    __repr__ = __str__

if __name__ == '__main__':
    import os
    os.chdir('tests')
    os.command('pytest test_config.py')
