#!/usr/bin/env python
# $Id$
'''     Downloader

A tools for downloading Splunk Enterprise packages.

References:

https://answers.splunk.com/answers/401395/is-there-a-way-to-write-a-script-to-download-the-l.html
https://answers.splunk.com/answers/401953/what-is-the-exact-raspberry-pi-debian-cli-command.html
https://github.com/kennethreitz/requests/issues/2022

wget -O - https://www.splunk.com/en_us/download/splunk-enterprise.html | grep -w handleDownload
'''

import re
import requests
from StringIO import StringIO
from c9r.app import Command
from c9r.pylog import logger


class Downloader(Command):
    '''This tool does not actually do the downloads for now: It only prints out a wget command
    that may be run to download packages. It does not check if a package is already downloaded
    either -- Those features may be implemented later.

    Configuration options:

      product_url	URL to the product information page.

      download_base	Base URL + path to the released package repositories.

      package_regex	A regex for parsing the product information page's HTML for
                        package information. It should contain only one value group that
                        produces the path to be used by the next regex to get details.

      path_regex	A regex for parsing the path found in the production information
                        page HTML to produce details on the current release of the product,
                        such as version and build identifiers.

      path		A format string for generating download paths to each package to be
                        downloaded, which concatenates to download_base above to generate
                        the full download URL.

      products          A list of products to download, keyed by individual product name.
                        For each product, a list keyed by OS names is expected to specify
                        what packages to download by providing format strings to generate
                        package file names.
    '''
    def_conf = "~/.etc/downloader-conf.json"

    def __init__(self):
        Command.__init__(self)
        self.regex = re.compile(self.config('package_regex'))
        self.repath = re.compile(self.config('path_regex'))

    def __call__(self):
        '''
        '''
        product = self.config('product_url')
        if product is None:
            logger.error('No product information page configured. Exiting.')
            return
        info = requests.get(self.config('product_url'))
        if info.status_code != 200:
            logger.error('Error getting product information: status = {0}'.format(info.status_code))
            return
        mp = None
        for line in StringIO(info.content):
            mx = self.regex.search(line)
            if mx is None: continue
            link = mx.group(1)
            logger.debug(link)
            mp = self.repath.search(link)
            if mp: break
        if mp is None:
            print('Did not find anything to download on page:\n\t{0}\n'.format(product))
            return
        pkginfo = mp.groupdict()
        path = self.config('download_base')+self.config('path')
        logger.debug('Product download folder: '+path)
        logger.debug('Retrieving configured packages: ----------')
        for prod, val in self.config('products').iteritems():
            pkginfo['product'] = prod
            for os, package in val.iteritems():
                for pkg in package if isinstance(package, list) else [package]:
                    pkginfo['os'] = os
                    link = (path+'/'+pkg).format(**pkginfo)
                    print('wget {0}'.format(link))
        

if __name__ == "__main__":
    Downloader()()
