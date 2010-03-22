"""
    The TestApp is wrapped into the middleware.

    >>> from playmobile.devices.wsgi import PlaymobileDeviceMiddleware

    >>> app = TestApp()
    >>> wrapped = PlaymobileDeviceMiddleware(app)

    The environment is set with an user agent string.

    >>> environ = {'HTTP_USER_AGENT': "Mozilla/5.0 (SymbianOS/9.1; U; [en]; Series60/3.0 NokiaE60/4.06.0) AppleWebKit/413 (KHTML, like Gecko) Safari/413"}
    >>> wrapped(environ, lambda *args: None)

    Now we can check that the environment contains some info about the device.

    >>> app.environ['playmobile.devices.marker_name']
    'IBasicDeviceType'
    >>> app.environ['playmobile.devices.marker']
    <InterfaceClass playmobile.interfaces.devices.IBasicDeviceType>

    >>> environ = {'HTTP_USER_AGENT': "Mozilla/5.0 (iPhone Simulator; U; CPU iPhone OS 3_1_3 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7E18 Safari/528.16"}
    >>> wrapped(environ, lambda *args: None)
    >>> app.environ['playmobile.devices.marker_name']
    'IAdvancedDeviceType'
    >>> app.environ['playmobile.devices.marker']
    <InterfaceClass playmobile.interfaces.devices.IAdvancedDeviceType>

"""


class TestApp(object):
    """ it only sets the environ attribute. So we can verify some expectations
    on it.
    """

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response('200 Ok', [('Content-Type', 'text/plain')])


