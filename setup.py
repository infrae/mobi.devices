#!/usr/bin/env python

import os
from setuptools import setup, find_packages

print find_packages('src')

setup(name='mobi.devices',
      version='0.1dev',
      description='Mobile Device management',
      author='Infrae',
      author_email='info@infrae.com',
      url='infrae.com',
      package_dir={'': 'src'},
      package_data={'mobi.devices': ['data']},
      packages=find_packages('src'),
      namespace_packages=['mobi'],
      install_requires=[
        'zope.interface',
        'mobi.interfaces',
        'mobi.caching',
        'pywurfl>=7.0.0',
        'webob'
      ],
      tests_requires=[
        'nose',
      ],
      test_suite='nose.collector',
      entry_points = {
        'paste.filter_factory': [
            'classifier = '
              'mobi.devices.wsgi.devicedetection:'
              'device_middleware_filter_factory',
            'router = '
              'mobi.devices.wsgi.router:'
              'router_middleware_filter_factory']}
      )
