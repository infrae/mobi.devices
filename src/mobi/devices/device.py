# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
from zope.interface import implements
from mobi.interfaces.devices import (IDevice,
    IStandardDeviceType, IAdvancedDeviceType, IBasicDeviceType)


class Device(object):
    implements(IDevice)

    def __init__(self, user_agent, type_, platform=u"computer"):
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


