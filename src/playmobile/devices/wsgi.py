from webob import Request

from playmobile.devices.classifiers import get_device
from playmobile.caching import Cache
from playmobile.interfaces.devices import (
    IBasicDeviceType, IStandardDeviceType, IAdvancedDeviceType)


import logging
logger = logging.getLogger('playmobile.devices.wsgi')

_marker = object()

class PlaymobileDeviceMiddleware(object):
    """ The middleware aims at detecting devices type from User agents.
    Once found a cookie is set to cache the result for later queries.
    
    In debugging mode the GET parameter "PARAM_NAME" can be manually set
    to simulate device detection. It can then be disabled by setting it to
    "off".
    """

    cache_engine = Cache(
        namespace=__module__)
    cache = cache_engine.cache

    PARAM_NAME = '__dt'

    mapping = [
        ('advanced', IAdvancedDeviceType),
        ('standard', IStandardDeviceType),
        ('basic', IBasicDeviceType),
    ]

    reverse_mapping = map(lambda (a,b,): (b,a,), mapping)

    def __init__(self, app, debug=False):
        self.debug = debug
        if self.debug:
            logger.info('PlaymobileDeviceMiddleware start in debug mode.')
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        dtype = (self.debug and self.device_type_from_get_params(request)) or \
            self.device_type_from_cookie(request) or \
            self.device_type_from_user_agent(request)

        request.environ['playmobile.devices.marker'] = dtype
        request.environ['playmobile.devices.marker_name'] = dtype.__name__
        response = request.get_response(self.app)
        self.set_device_type_on_cookie(response, dtype)
        start_response(response.status,
            [a for a in response.headers.iteritems()])
        return response.app_iter

    def device_type_from_cookie(self, request):
        cookie_val = request.cookies.get(self.PARAM_NAME)
        dtype = dict(self.mapping).get(cookie_val)
        return dtype

    def device_type_from_get_params(self, request):
        param = request.GET.get(self.PARAM_NAME)
        if param == 'off':
            return self.device_type_from_user_agent(request)

        dtype = dict(self.mapping).get(param)
        if dtype is not None:
            logger.debug('device manually set to %s' % dtype.__name__)
        return dtype

    def device_type_from_user_agent(self, request):
        ua = request.environ.get('HTTP_USER_AGENT', '')
        logger.debug("get device from UserAgent: %s" % ua)
        device = self.cache('select_ua:%s' % ua, lambda : get_device(ua))
        return device.get_type()

    def set_device_type_on_cookie(self, response, dtype):
        val = dict(self.reverse_mapping).get(dtype, IBasicDeviceType)
        cookie_val = response.request.cookies.get(self.PARAM_NAME)
        if cookie_val is None or \
                cookie_val != dict(self.reverse_mapping).get(dtype, _marker):
            response.set_cookie(self.PARAM_NAME, val,
                max_age=10000000, path='/', secure=False)


def device_middleware_filter_factory(global_conf, **local_conf):
    def filter(app):
        debug = global_conf.get('debug', False)
        return PlaymobileDeviceMiddleware(app, debug)
    return filter


