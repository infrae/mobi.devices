from webob import Request

from playmobile.devices.classifiers import MITClassifier, WurflClassifier
from playmobile.devices.device import Device
from playmobile.caching import Cache
from playmobile.interfaces.devices import (
    IBasicDeviceType, IStandardDeviceType, IAdvancedDeviceType)


import logging
import base64
try:
    # Python 2.6
    import json
except ImportError:
    import simplejson as json

logger = logging.getLogger('playmobile.devices.wsgi')

_marker = object()

def serialize_cookie(data):
    return base64.b64encode(json.dumps(data))

def deserialize_cookie(data):
    return json.loads(base64.b64decode(data) or '{}')

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

    PARAM_NAME = '__devinfo'

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
        self.classifiers = [MITClassifier(), WurflClassifier()]

    def __call__(self, environ, start_response):
        request = Request(environ)
        device = (self.debug and self.device_from_get_params(request)) or \
            self.device_from_cookie(request) or \
            self.device_from_user_agent(request)

        if device is not None:
            dtype = device.get_type() or IBasicDeviceType
            request.environ['playmobile.devices.marker'] = dtype
            request.environ['playmobile.devices.marker_name'] = dtype.__name__
            request.environ['playmobile.devices.platform'] = \
                device.get_platform()

        response = request.get_response(self.app)

        logger.info('device: %s - %s' % (dtype.__name__, device.get_platform(),))

        if device is not None:
            self.set_device_on_cookie(response, device)

        start_response(response.status,
            [a for a in response.headers.iteritems()])
        return response.app_iter

    def device_from_cookie(self, request):
        data = request.cookies.get(self.PARAM_NAME, None)
        if data is not None:
            cookie_val = deserialize_cookie(data)
            dtype = dict(self.mapping).get(cookie_val['type'],
                IBasicDeviceType)
            return Device(request.environ.get('HTTP_USER_AGENT'),
                dtype, platform=cookie_val['platform'])
        return None

    def device_from_get_params(self, request):
        param = request.GET.get(self.PARAM_NAME)
        if param == 'off':
            return self.device_from_user_agent(request)

        dtype = dict(self.mapping).get(param)
        if dtype is not None:
            logger.debug('device manually set to %s' % dtype.__name__)
        return Device(request.environ.get('HTTP_USER_AGENT'), dtype)

    def device_from_user_agent(self, request):
        ua = request.environ.get('HTTP_USER_AGENT', '')
        logger.debug("get device from UserAgent: %s" % ua)
        device = self.cache('select_ua:%s' % ua, lambda : self._get_device(ua))
        return device

    def set_device_on_cookie(self, response, device):
        type_val = dict(self.reverse_mapping).get(device.get_type(),
            'basic')
        data = {'type': type_val, 'platform': device.get_platform()}
        encdata = response.request.cookies.get(self.PARAM_NAME)
        if encdata is None or \
                deserialize_cookie(encdata) != data:
            response.set_cookie(self.PARAM_NAME,
                serialize_cookie(data),
                max_age=10000000, path='/', secure=False)

    def _get_device(self, ua):
        for classifier in self.classifiers:
            device = classifier(ua)
            if device is not None: return device
        return Device(ua, IBasicDeviceType)


def device_middleware_filter_factory(global_conf, **local_conf):
    def filter(app):
        debug = global_conf.get('debug', False) or \
            local_conf.get('debug', False)
        return PlaymobileDeviceMiddleware(app, debug)
    return filter


