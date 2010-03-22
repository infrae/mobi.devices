from zope.interface import implements

from playmobile.interfaces.devices import (IDevice, IClassifier,
    IStandardDeviceType, IAdvancedDeviceType, IBasicDeviceType)
from playmobile.devices.wurfl import devices
from pywurfl.algorithms import JaroWinkler
from pywurfl.exceptions import DeviceNotFound

from playmobile.devices.device import Device, WDevice

import os, re


import logging
logger = logging.getLogger('playmobile.devices.classifiers')

try:
    # Python 2.6
    import json
except ImportError:
    import simplejson as json


class WurflClassifier(object):
    implements(IClassifier)

    def __init__(self, user_agent):
        self.user_agent = user_agent

    def __call__(self):
        try:
            logger.debug("Lookup the user agent against wurfl db.")
            wurfl_device = \
                devices.select_ua(self.user_agent,
                    search=JaroWinkler(accuracy=0.85))
            return WDevice(wurfl_device)
        # this is bad but a weird but makes DeviceNotFound not catched if
        # except DeviceNotFound is used
        except Exception as e:
            logger.debug("Error during wurfl lookup :%s" % str(e))
        return None


class MITUAPatternMatcher(object):

    pattern_file_path = ('..', '..', '..', 'data',
        'MIT', 'device_user_agent_patterns.json')

    def __init__(self):
        self.__patterns = []

    def load_patterns(self):
        filename = os.path.join(os.path.dirname(__file__),
            *self.pattern_file_path)
        fd = open(filename, 'r')
        try:
            data = json.load(fd)
            for item in data:
                item['pattern'] = self.__make_regex(item['pattern'])
            self.__patterns = data
        finally:
            fd.close()

    def lookup(self, ua):
        # The order of the patterns is important
        for dev_info in self.__patterns:
            pattern = dev_info['pattern']
            if re.match(pattern, ua):
                logger.debug("User Agent matched %s in MIT pattern list" %
                    str(pattern))
                logger.debug("Device info : %s" % dev_info)
                return dev_info
        logger.debug("Device lookup failed in MIT db.")
        return None

    def __make_regex(self, pattern_string):
        """ User agent in data can be either a regex e.g: /Opera/ or a string
        Opera. A string will be converted to a regex like this :

            Opera -> r/^Opera/

        which is what we want.
        """
        return re.compile(pattern_string)


mit_matcher = MITUAPatternMatcher()
mit_matcher.load_patterns()


class MITClassifier(object):
    implements(IClassifier)

    patterns = mit_matcher

    def __init__(self, user_agent):
        self.user_agent = user_agent

    def __call__(self):
        device_infos = self.patterns.lookup(self.user_agent)
        if device_infos is None:
            return None

        device_type = device_infos['device_type']
        if device_type == 'Webkit':
            return Device(IAdvancedDeviceType)
        elif device_type == 'Touch':
            return Device(IStandardDeviceType)
        else:
            return Device(IBasicDeviceType)


def get_device(ua):
    device = MITClassifier(ua)()
    if device is None:
        device = WurflClassifier(ua)()
    if device is None:
        device = Device(IBasicDeviceType)
    return device


