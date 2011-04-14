#!/usr/bin/env python

import os
from setuptools import setup, find_packages

VERSION='1.2'
tests_require = []

install_requirements = [
    'Beaker',
    'mobi.interfaces',
    'webob',
    'zope.interface',
]

# add simplejson requirement in json not available in python
try:
    import json
except ImportError:
    install_requirements.append('simplejson')


setup(name='mobi.devices',
      version=VERSION,
      dependency_links=['http://dist.infrae.com/thirdparty'],
      description='Mobile Device detection library and wsgi middlewares',
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      author='Antonin Amand at Infrae',
      author_email='info@infrae.com',
      license="BSD",
      url='http://mobi.infrae.com/',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['mobi'],
      install_requires=install_requirements,
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      test_suite='mobi.devices.tests',
      entry_points = {
        'paste.filter_factory': [
            'classifier = '
              'mobi.devices.wsgi.devicedetection:'
                'device_middleware_filter_factory',
            'router = '
              'mobi.devices.wsgi.router:'
                'router_middleware_filter_factory']}
      )
