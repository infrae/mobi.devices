#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='playmobile.devices',
      version='0.1dev',
      description='Mobile Device management',
      author='Infrae',
      author_email='info@infrae.com',
      url='infrae.com',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['playmobile'],
      install_requires=[
        'zope.interface',
        'playmobile.interfaces',
        'pywurfl',
      ],
     )
