#!/usr/bin/env python
#
#       Setup for the c9r Python module.
#

import sys
from setuptools import setup

def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def tar(file, filelist, expression='^.+$'):
    """
    tars dir/files into file, only tars file that match expression
    """

    tar = tarfile.TarFile(file, 'w')
    try:
        for element in filelist:
            try:
                for file in listdir(element, expression, add_dirs=True):
                    tar.add(os.path.join(element, file), file, False)
            except:
                tar.add(element)
    finally:
        tar.close()


def start():
    if 'sdist' in sys.argv:
        tar(['app.py', 'cli.py', '__init__.py', 'jsonpy.py', 'setup.py'])

    setup(name='c9r',
          version='0.1',
          description="""Python utility modules in the 'c9r' namespace.""",
          long_description="""
        Utility modules in the 'c9r' namespace, including IP networking, etc.
        """,
          author='Wei Wang',
          author_email='ww@9rivers.com',
          license='https://github.com/ww9rivers/c9r/wiki/License',
          classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "License :: OSI Approved :: MIT License",],
          url='https://github.com/ww9rivers/c9r',
          platforms='Windows, Linux, Mac, Unix',
          packages=['html',
                    'mail',
                    'net',
                    'snmp',
                    '.'
                    ],
          )

if __name__ == '__main__':
    start()
