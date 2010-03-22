from playmobile.devices.classifiers import get_device
from playmobile.caching import Cache

import logging
logger = logging.getLogger('playmobile.devices.wsgi')

# In your pastie ini file add :
# log_stream = sys.stdout
# log_level = logging.DEBUG

class DebugDeviceMiddleware(object):

    DEBUG_DEVICE_TYPE = None

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print "Device middleware is in debug mode."
        dtype = self.get_from_params(environ['QUERY_STRING'])
        if dtype is not None:
            logger.debug('DEBUG MODE: Device manually set to %s' %
                dtype.__name__)
            environ['playmobile.devices.marker'] = dtype
            environ['playmobile.devices.marker_name'] = dtype.__name__
            return self.app(environ, start_response)
        return PlaymobileDeviceMiddleware(self.app)(environ, start_response)

    def get_from_params(self, query_string):
        from cgi import parse_qs
        from playmobile.interfaces.devices import (
            IBasicDeviceType, IStandardDeviceType, IAdvancedDeviceType)
        params = parse_qs(query_string)
        self.DEBUG_DEVICE_TYPE = params.get('dt', [None])[0] \
            or self.DEBUG_DEVICE_TYPE
        if self.DEBUG_DEVICE_TYPE == 'basic':
            return IBasicDeviceType
        elif self.DEBUG_DEVICE_TYPE == 'standard':
            return IStandardDeviceType
        elif self.DEBUG_DEVICE_TYPE == 'advanced':
            return IAdvancedDeviceType
        elif self.DEBUG_DEVICE_TYPE in ['off', 'false', 'disable']:
            self.DEBUG_DEVICE_TYPE = None

        return None


class PlaymobileDeviceMiddleware(object):

    cache_engine = Cache(
        namespace='playmobile.devices.PlaymobileDeviceMiddleware')
    cache = cache_engine.cache

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        ua = environ.get('HTTP_USER_AGENT', '')
        logger.debug("UserAgent: %s" % ua)
        device = self.cache('select_ua:%s' % ua, lambda : get_device(ua))
        dtype = device.get_type()
        environ['playmobile.devices.marker'] = dtype
        environ['playmobile.devices.marker_name'] = dtype.__name__
        print dtype.__name__
        return self.app(environ, start_response)


def device_middleware_filter_factory(global_conf, **local_conf):
    def filter(app):
        if global_conf.get('debug', False):
            return DebugDeviceMiddleware(app)
        else:
            return PlaymobileDeviceMiddleware(app)
    return filter


