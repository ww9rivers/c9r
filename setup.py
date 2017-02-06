#!/usr/bin/env python
#
#       Setup for the c9r Python module.
#

from setuptools import setup

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
                'snmp'
                ],

      install_requires=[
        'gevent'
        ],
      )
