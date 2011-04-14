# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
from webob import Request

from mobi.devices.classifiers import MITClassifier, WurflClassifier
from mobi.devices.device import Device
from mobi.interfaces.devices import (
    IBasicDeviceType, IStandardDeviceType, IAdvancedDeviceType)

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

import logging
import base64
try:
    import json
except ImportError:
    import simplejson as json

logger = logging.getLogger('mobi.devices.wsgi')

_marker = object()

def serialize_cookie(data):
    return base64.b64encode(json.dumps(data))


def deserialize_cookie(data):
    try:
        return json.loads(base64.b64decode(data) or '{}')
    except (Exception,), e:
        logger.warn('error while deserializing cookie : %s' % str(e))
        return None


class MobiDeviceMiddleware(object):
    """ The middleware aims at detecting devices type from User agents.
    Once found a cookie is set to cache the result for later queries.

    In debugging mode the GET parameter "PARAM_NAME" can be manually set
    to simulate device detection. It can then be disabled by setting it to
    "off".
    """

    PARAM_NAME = '__devinfo'

    _mapping = [
        ('advanced', IAdvancedDeviceType),
        ('standard', IStandardDeviceType),
        ('basic', IBasicDeviceType),
    ]

    DEFAULT_CACHE_OPTIONS = {
        'cache.type': 'memory',
        'cache.lock_dir': '/tmp',
        'cache.max_items': 1000,
    }

    mapping = dict(_mapping)
    reverse_mapping = dict(map(lambda (a,b,): (b,a,), _mapping))

    def __init__(self, app,
                 cookie_cache=True,
                 cache_opts=None,
                 debug=False,
                 cookie_max_age=0,
                 classifiers=[]):
        self.debug = debug
        self.cookie_cache = cookie_cache
        cache_manager = CacheManager(
            **parse_cache_config_options(cache_opts or
                                         self.DEFAULT_CACHE_OPTIONS))
        self.cache = cache_manager.get_cache('mobi.devices')

        if self.debug:
            logger.info('MobiDeviceMiddleware start in debug mode.')
        self.app = app
        self.set_cookie_max_age(int(cookie_max_age))
        self.classifiers = classifiers if isinstance(classifiers, list) \
                else [classifiers]

    def __call__(self, environ, start_response):
        request = Request(environ)
        device = self.device_from_get_params(request) or \
            self.device_from_cookie(request) or \
            self.device_from_user_agent(request)

        if device is not None:
            self.set_device_on_request(request, device)

        response = request.get_response(self.app)

        logger.info('device: %s - %s' %
            (device.type, device.platform))

        if device is not None:
            self.set_device_on_cookie(response, device)

        start_response(response.status,
            [a for a in response.headers.iteritems()])
        return response.app_iter

    def set_cookie_max_age(self, max_age):
        if max_age <= 0:
            self._cookie_max_age = None
        else:
            self._cookie_max_age = max_age

    def set_device_on_request(self, request, device):
        dtype = device.type or IBasicDeviceType
        platform = device.platform or 'computer'

        request.environ['mobi.devices.device'] = device
        request.environ['mobi.devices.type'] = \
            self.reverse_mapping[dtype]
        request.environ['mobi.devices.marker'] = dtype
        request.environ['mobi.devices.marker_name'] = dtype.__name__
        request.environ['mobi.devices.platform'] = platform

    def device_from_cookie(self, request):
        if not self.cookie_cache:
            return None
        data = request.cookies.get(self.PARAM_NAME, None)
        if data is not None:
            cookie_val = deserialize_cookie(data)
            if cookie_val is None:
                return None
            dtype = self.mapping.get(cookie_val['type'],
                IBasicDeviceType)
            return Device(request.environ.get('HTTP_USER_AGENT'),
                dtype, platform=cookie_val['platform'])
        return None

    def device_from_get_params(self, request):
        if not self.debug: return None

        param = request.GET.get(self.PARAM_NAME)
        if param == 'off':
            return self.device_from_user_agent(request)

        dtype = self.mapping.get(param)
        platform = request.GET.get(self.PARAM_NAME + '_platform', '')
        if dtype is not None:
            logger.info('device manually set to %s' % dtype.__name__)
            return Device(request.environ.get('HTTP_USER_AGENT'),
                dtype, platform)
        return None

    def device_from_user_agent(self, request):
        ua = request.environ.get('HTTP_USER_AGENT', '')
        logger.info("get device from UserAgent: %s" % ua)

        def get_device():
            return self._get_device(ua)

        device = self.cache.get(key="device_lookup:%s" % ua,
                                createfunc=get_device)
        return device

    def set_device_on_cookie(self, response, device):
        if not self.cookie_cache:
            return
        type_val = self.reverse_mapping.get(device.type,
            'basic')
        data = {'type': type_val, 'platform': device.platform}
        encdata = response.request.cookies.get(self.PARAM_NAME)
        if encdata is None or \
                deserialize_cookie(encdata) != data:
            response.set_cookie(self.PARAM_NAME,
                                serialize_cookie(data),
                                max_age=self._cookie_max_age,
                                path='/', secure=False)

    def _get_device(self, ua):
        for classifier in self.classifiers:
            device = classifier(ua)
            if device is not None:
                return device
        return Device(ua, IBasicDeviceType)


def device_middleware_filter_factory(global_conf, **local_conf):
    def filter(app):
        debug = global_conf.get('debug', False) or \
            local_conf.get('debug', False)
        cookie_max_age = int(local_conf.get('cookie_max_age', 0))
        cookie_cache = local_conf.get('cookie_cache', not(debug))
        cache_options = {}
        for key, value in local_conf.iteritems():
            if key.startswith('cache'):
                cache_options[key] = value

        wurfl_config = {}
        var = local_conf.get('var', None),
        wurfl_file = local_conf.get('wurfl_file', None)
        if wurfl_file is not None:
            wurfl_config['wurfl_file'] = wurfl_file
        if var is not None:
            wurfl_config['var'] = var
        classifiers = [MITClassifier(), WurflClassifier(wurfl_config)]
        return MobiDeviceMiddleware(app,
                                    debug=debug,
                                    cookie_cache=cookie_cache,
                                    cache_opts=cache_options,
                                    cookie_max_age=cookie_max_age,
                                    classifiers=classifiers)
    return filter

