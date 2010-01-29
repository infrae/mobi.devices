#!/usr/bin/env python

from distutils.core import setup

setup(name='playmobile.devices',
      version='0.1dev',
      description='Mobile Device management',
      author='Infrae',
      author_email='info@infrae.com',
      url='infrae.com',
      packages=["playmobile", "playmobile.devices"],
      install_requires=[
        'distutils',
        'zope.interface',
        'playmobile.interfaces',
        'pywurfl',
      ],
     )
