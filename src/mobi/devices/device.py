from zope.interface import implements
from mobi.interfaces.devices import (IDevice,
    IStandardDeviceType, IAdvancedDeviceType, IBasicDeviceType)
from mobi.devices import PLATFORMS
from mobi.devices.wurfl import devices as wdevices

class Device(object):
    implements(IDevice)

    def __init__(self, user_agent, type_, platform=""):
        self.user_agent = user_agent
        self.type = type_
        self.platform = unicode(platform)


class MITDevice(object):
    implements(IDevice)

    def __init__(self, user_agent, info):
        self.user_agent = user_agent
        self.info = info
        self.type = self._get_type()
        self.platform = self._get_platform()

    def _get_type(self):
        device_type = self.info['device_type']
        if device_type == 'Webkit':
            return IAdvancedDeviceType
        elif device_type == 'Touch':
            return IStandardDeviceType
        elif device_type == 'Basic':
            return IBasicDeviceType
        return None

    def _get_platform(self):
        return unicode(self.info.get('platform', ''))


class WDevice(object):
    implements(IDevice)

    def __init__(self, user_agent, wurfl_device):
        self.user_agent = user_agent
        self.type = self._get_type(wurfl_device)
        self.platform = self._get_platform(wurfl_device)

    def _get_platform(self, wurfl_device):
        platform = None
        if wurfl_device.is_wireless_device:
            platform_names = PLATFORMS.keys()
            os = wurfl_device.device_os
            for name in platform_names:
                if name in os:
                    return name
            return u'featurephone'
        else:
            fallbacks = self._fallback_devices(wurfl_device)
            for fallback in fallbacks:
                if 'bot' in fallback.devid or \
                        fallback.devid == 'generic_web_crawler':
                    return u'spider'
            return u'computer'

    def _fallback_devices(self, wurfl_device):
        device = wurfl_device
        fallbacks = []
        while wdevices.devids.has_key(device.fall_back):
            device = wdevices.devids[device.fall_back]
            fallbacks.append(device)
        return fallbacks

    def _get_type(self, wurfl_device):
        support_level = int(wurfl_device.xhtml_support_level)

        if support_level >= 4:
            return IAdvancedDeviceType
        elif support_level == 3:
            return IStandardDeviceType
        else:
            return IBasicDeviceType

