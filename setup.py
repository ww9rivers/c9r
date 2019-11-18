#!/usr/bin/env python3
#
#       Setup for the c9r Python module.
#

from setuptools import setup

<<<<<<< HEAD

setup(name='c9r',
      version='0.2.3',
=======
setup(name='c9r',
      version='0.1',
>>>>>>> parent of eecdaf7... Revised to use Python setuptools packaging.
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
<<<<<<< HEAD
      packages=[
          'c9r', 'c9r/cli', 'c9r/csvx', 'c9r/file', 'c9r/mail', 'c9r/net',
          'c9r/pim', 'c9r/text',
          'c9r/util', 'c9r/util/filter',
      ],
      package_data={
        'c9r/util':
            [
            'c9r/util/csvfix-conf-EMPF2.json',
            'c9r/util/csvfix-conf.json'
            ]
        },
=======
      packages=['html',
                'mail',
                'net',
                'snmp'
                ],
>>>>>>> parent of eecdaf7... Revised to use Python setuptools packaging.

      install_requires=[
          'gevent',
          'paramiko',
          'pysnmp',
          'requests'
        ],
<<<<<<< HEAD
      include_package_data=True,

      #
      # ----    Test using nosetests:  python ./setup.py nosetests
      #
      # Ref.: http://python-packaging.readthedocs.io/en/latest/testing.html
      #
      #test_suite='pytest',
      tests_require=['pytest'],
      setup_requires=['pytest-runner'],
      zip_safe=False)
=======
      )
>>>>>>> parent of eecdaf7... Revised to use Python setuptools packaging.
