#!/usr/bin/env python

import os
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
        'playmobile.caching',
        'pywurfl>=7.0.0',
        'nose',
        'webob'
      ],
      test_suite='nose.collector',
      entry_points = {
        'paste.filter_factory': [
            'classifier = '
              'playmobile.devices.wsgi.devicedetection:'
              'device_middleware_filter_factory',
            'router = '
              'playmobile.devices.wsgi.router:'
              'router_middleware_filter_factory']}
      )
