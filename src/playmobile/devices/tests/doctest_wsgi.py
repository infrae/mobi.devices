"""
    The TestApp is wrapped into the middleware.

    >>> from playmobile.devices.wsgi import PlaymobileDeviceMiddleware

    >>> app = TestApp()
    >>> wrapped = PlaymobileDeviceMiddleware(app)

    The environment is set with an user agent string.

    >>> environ = {'User-Agent': "Mozilla/5.0 (SymbianOS/9.1; U; [en]; Series60/3.0 NokiaE60/4.06.0) AppleWebKit/413 (KHTML, like Gecko) Safari/413"}
    >>> wrapped(environ, lambda *args: None)

    Now we can check that the environment contains some info about the device.

    >>> app.environ['playmobile.devices.marker_name']
    'IStandardDeviceType'
    >>> app.environ['playmobile.devices.marker']
    <InterfaceClass playmobile.interfaces.devices.IStandardDeviceType>

"""


class TestApp(object):
    """ it only sets the environ attribute. So we can verify some expectations
    on it.
    """

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response('200 Ok', [('Content-Type', 'text/plain')])

if __name__ == '__main__':
        import doctest
        doctest.testmod()
