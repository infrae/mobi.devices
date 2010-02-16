from playmobile.devices.classifiers import get_device
from playmobile.caching import Cache

class DebugDeviceMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print "Device middleware is in debug mode."
        dtype = self.get_from_params(environ['QUERY_STRING'])
        if dtype:
            print 'Device manually set to %s' % dtype.__name__
            environ['playmobile.devices.marker'] = dtype
            environ['playmobile.devices.marker_name'] = dtype.__name__
            return self.app(environ, start_response)
        return PlaymobileDeviceMiddleware(self.app)(environ, start_response)

    def get_from_params(self, query_string):
        from cgi import parse_qs
        from playmobile.interfaces.devices import (
            IBasicDeviceType, IStandardDeviceType, IAdvancedDeviceType)
        params = parse_qs(query_string)
        device_type = params.get('dt', [None])[0]
        if device_type == 'basic':
            return IBasicDeviceType
        elif device_type == 'standard':
            return IStandardDeviceType
        elif device_type == 'advanced':
            return IAdvancedDeviceType
        return None


class PlaymobileDeviceMiddleware(object):

    cache_engine = Cache(
        namespace='playmobile.devices.PlaymobileDeviceMiddleware')
    cache = cache_engine.cache

    def __init__(self, app, debug=False):
        self.app = app
        self.debug = debug
        if self.debug:
            print "device middleware started in debug mode."

    def __call__(self, environ, start_response):
        ua = environ.get('User-Agent', '')
        device = self.cache('select_ua', lambda : get_device(ua))
        dtype = device.get_type()
        environ['playmobile.devices.marker'] = dtype
        environ['playmobile.devices.marker_name'] = dtype.__name__
        return self.app(environ, start_response)


def device_middleware_filter_factory(global_conf, **local_conf):
    def filter(app):
        if global_conf.get('debug', False):
            return DebugDeviceMiddleware(app)
        else:
            return PlaymobileDeviceMiddleware(app)
    return filter
