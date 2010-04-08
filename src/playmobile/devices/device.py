from zope.interface import implements
from playmobile.interfaces.devices import (IDevice,
    IStandardDeviceType, IAdvancedDeviceType, IBasicDeviceType)


class Device(object):
    implements(IDevice)

    def __init__(self, type_):
        self.type = type_

    def get_type(self):
        return self.type


class MITDevice(object):
    implements(IDevice)

    def __init__(self, info):
        self.info = info

    def get_type(self):
        device_type = self.info['device_type']
        if device_type == 'Webkit':
            return IAdvancedDeviceType
        elif device_type == 'Touch':
            return IStandardDeviceType
        elif device_type == 'Basic':
            return IBasicDeviceType
        return None

    def get_platform(self):
        return self.info.get('platform')


class WDevice(object):
    implements(IDevice)

    def __init__(self, wurfl_device):
        self.wurfl_device = wurfl_device
        self.__device_type = None

    def get_platform(self):
        pass

    def get_type(self):
        if self.__device_type:
            return self.__device_type
        support_level = int(self.wurfl_device.xhtml_support_level)

        if support_level == 4:
            self.__device_type = IAdvancedDeviceType
        elif support_level == 3:
            self.__device_type = IStandardDeviceType
        else:
            self.__device_type = IBasicDeviceType

        return self.__device_type
