from playmobile.devices.classifiers import get_device
from playmobile.caching import Cache


class PlaymobileDeviceMiddleware(object):

    cache_engine = Cache(
        namespace='playmobile.devices.PlaymobileDeviceMiddleware')
    cache = cache_engine.cache

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        ua = environ.get('User-Agent', '')
        device = self.cache('select_ua', lambda : get_device(ua))
        environ['playmobile.devices.marker'] = device.get_type()
        environ['playmobile.devices.marker_name'] = device.get_type().__name__
        return self.app(environ, start_response)

