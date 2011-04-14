# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
"""
    The TestApp is wrapped into the middleware.

    >>> from mobi.devices.wsgi.devicedetection\\
    ...   import MobiDeviceMiddleware
    >>> from mobi.devices.wsgi.devicedetection\\
    ...   import serialize_cookie, deserialize_cookie

    >>> from mobi.devices.classifiers import MITClassifier

    >>> classifiers = [MITClassifier()]

    >>> app = TestApp()
    >>> wrapped = MobiDeviceMiddleware(app, classifiers=classifiers)

    The environment is set with an user agent string.

    >>> from webob import Request
    >>> request = Request.blank('/')
    >>> request.environ['HTTP_USER_AGENT'] = "Mozilla/5.0 (SymbianOS/9.1;" \\
    ...     " U; [en]; Series60/3.0 NokiaE60/4.06.0) AppleWebKit/413" \\
    ...     " (KHTML, like Gecko) Safari/413"
    >>> request.call_application(wrapped) #doctest: +ELLIPSIS
    ('200 Ok..., ['hello!'])

    Now we can check that the environment contains some info about the device.

    >>> app.environ['mobi.devices.marker_name']
    'IBasicDeviceType'
    >>> app.environ['mobi.devices.marker']
    <InterfaceClass mobi.interfaces.devices.IBasicDeviceType>

    >>> request = Request.blank('/')
    >>> request.environ['HTTP_USER_AGENT'] = "Mozilla/5.0 (iPhone" \\
    ...     " Simulator; U; CPU iPhone OS 3_1_3 like Mac OS X; en-us)" \\
    ...     " AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0" \\
    ...     " Mobile/7E18 Safari/528.16"
    >>> request.call_application(wrapped) #doctest: +ELLIPSIS
    ('200 Ok..., ['hello!'])
    >>> app.environ['mobi.devices.marker_name']
    'IAdvancedDeviceType'
    >>> app.environ['mobi.devices.marker']
    <InterfaceClass mobi.interfaces.devices.IAdvancedDeviceType>

    When the response returns the middle sets a cookie to cache the result
    on the client side.

    >>> request = Request.blank('/')
    >>> response = request.get_response(wrapped)
    >>> response.headers['Set-Cookie'] # doctest: +ELLIPSIS
    '__devinfo="eyJwbGF0Zm9ybSI6ICJjb21wdXRlciIsICJ0eXBlIjogImJhc2ljIn0\\\\075"; Path=/'

    We can set a max-age:
    >>> wrapped.set_cookie_max_age(10000)
    >>> request = Request.blank('/')
    >>> response = request.get_response(wrapped)
    >>> response.headers['Set-Cookie'] # doctest: +ELLIPSIS
    '__devinfo="eyJwbGF0Zm9ybSI6ICJjb21wdXRlciIsICJ0eXBlIjogImJhc2ljIn0\\\\075"; expires="..."; Max-Age=10000; Path=/'
    >>> cookie = response.headers['Set-Cookie']


    When client sends a cookie it is used as a cache.

    >>> request = Request.blank('/')
    >>> request.environ['HTTP_COOKIE'] = cookie
    >>> response = request.get_response(wrapped)
    >>> response.headers.get('Set-Cookie', None) is None
    True
    >>> app.environ['mobi.devices.marker_name']
    'IBasicDeviceType'
    >>> app.environ['mobi.devices.marker']
    <InterfaceClass mobi.interfaces.devices.IBasicDeviceType>
    >>> app.environ['mobi.devices.platform']
    u'computer'

    When client use a malformed cookie it doesn't fail.

    >>> request = Request.blank('/')
    >>> request.environ['HTTP_COOKIE'] = '__devinfo=10931280391823asd=='
    >>> response = request.get_response(wrapped)


"""


class TestApp(object):
    """ it only sets the environ attribute. So we can verify some expectations
    on it.
    """
    environ = {}

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response('200 Ok', [('Content-Type', 'text/plain')])
        return ['hello!']


import shutil
import os
from mobi.devices.wurfl.parser import Device

data_dir = os.path.join(os.path.dirname(__file__), 'var')
config = {
    'var': data_dir
}

def setup(test):
    teardown(test)
    try:
        os.mkdir(data_dir)
    except OSError:
        pass

def teardown(test):
    try:
        if Device.db:
            Device.db.close()
        shutil.rmtree(data_dir)
    except:
        pass

def test_suite():
    import unittest
    import doctest

    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite(__name__, setUp=setup, tearDown=teardown))
    return suite
