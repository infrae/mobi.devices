#!/usr/bin/env python

import os
from setuptools import setup, find_packages

VERSION='1.0b1'
tests_require = ['Nose',]

setup(name='mobi.devices',
      version=VERSION,
      dependency_links=['http://dist.infrae.com/thirdparty'],
      description='Mobile Device detection',
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      author='Antonin Amand',
      author_email='info@infrae.com',
      license="BSD",
      url='http://infrae.com/',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['mobi'],
      install_requires=[
        'mobi.caching',
        'mobi.interfaces',
        'python-Levenshtein',
        'pywurfl>=7.0.0',
        'webob',
        'zope.interface',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
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
