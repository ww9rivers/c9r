#!/usr/bin/env python
#
#       Setup for the c9r Python module.
#

from setuptools import setup


setup(name='c9r',
      version='0.2.0',
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
        "License :: OSI Approved :: MIT License"],
      url='https://github.com/ww9rivers/c9r',
      platforms='Windows, Linux, Mac, Unix',
      packages=[
        'c9r', 'c9r/cli', 'c9r/csv', 'c9r/file', 'c9r/html', 'c9r/mail', 'c9r/net',
        'c9r/pim',
        'c9r/util', 'c9r/util/filter',
        ],
      package_data={
        'c9r/util':
            [
            'c9r/util/csvfix-conf-EMPF2.json',
            'c9r/util/csvfix-conf.json'
            ]
        },

      install_requires=[
        'gevent',
        'requests'
        ],
      include_package_data=True,
      # test_suite='nose.collector',
      # tests_require=['nose'],
      zip_safe=False)
