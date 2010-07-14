from zope.interface import implements

from playmobile.interfaces.devices import (IDevice, IClassifier,
    IStandardDeviceType, IAdvancedDeviceType, IBasicDeviceType)
from playmobile.devices.wurfl import devices
from pywurfl.algorithms import JaroWinkler, LevenshteinDistance
from pywurfl.exceptions import DeviceNotFound

from playmobile.devices.device import MITDevice, WDevice
from playmobile.devices import DATA_DIR

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

    def __init__(self, accuracy=0.7, weight=0.01):
        self.accuracy = accuracy
        self.weight = weight

    def __call__(self, user_agent):
        try:
            logger.debug("Lookup the user agent against wurfl db.")
            wurfl_device = \
                devices.select_ua(unicode(user_agent),
                    search=JaroWinkler(accuracy=self.accuracy,
                        weight=self.weight))
            # logger.debug("Device found: %s" % wurfl_device)
            return WDevice(unicode(user_agent), wurfl_device)
        # this is bad but a weird but makes DeviceNotFound not catched if
        # except DeviceNotFound is used
        except Exception, e:
            logger.debug("Error during wurfl lookup :%s" % str(e))
        return None

class StringMatcher(object):
    def __init__(self, string):
        self.pattern = string

    def __call__(self, against):
        return (against.find(self.pattern) > -1)


class RegexMatcher(object):
    def __init__(self, string):
        self.pattern = re.compile(string)

    def __call__(self, against):
        return (self.pattern.search(against) is not None)


class MITUAPatternMatcher(object):

    pattern_file_paths = [
        'MIT/device_user_agent_patterns.json',
        'Infrae/device_user_agent_patterns.json',
    ]

    def __init__(self):
        self.__patterns = []

    def load_patterns(self):
        self.__patterns = []
        for path in self.pattern_file_paths:
            filepath = os.path.join(DATA_DIR, path)
            fd = open(filepath, 'r')
            try:
                data = json.load(fd)
                for item in data:
                    item['matcher'] = self.__build_matcher(item['pattern'])
                self.__patterns += data
            finally:
                fd.close()

    def lookup(self, ua):
        # The order of the patterns is important
        for dev_info in self.__patterns:
            matcher = dev_info['matcher']
            if matcher(ua):
                logger.debug("User Agent matched against MIT patterns")
                logger.debug("Device info : %s" % dev_info)
                return dev_info
        logger.debug("Device lookup failed in MIT db.")
        return None

    def __build_matcher(self, pattern_string):
        """ User agent in data can be either a regex e.g: /Opera/ or a string
        Opera. A string will be converted to a regex like this :

            Opera -> r/^Opera/
            /Opera/ -> r/Opera/
        """
        if pattern_string.startswith('/') and pattern_string.endswith('/'):
            return RegexMatcher(pattern_string[1:-1])
        return StringMatcher(pattern_string)


class MITClassifier(object):
    implements(IClassifier)

    def __init__(self):
        self.patterns = MITUAPatternMatcher()
        self.patterns.load_patterns()

    def __call__(self, user_agent):
        device_infos = self.patterns.lookup(user_agent)
        if device_infos is None:
            return None
        return MITDevice(unicode(user_agent), device_infos)


# USE FOR TEST PURPOSE ONLY
def get_device(ua):
    device = MITClassifier()(ua)
    if device is None:
        device = WurflClassifier()(ua)
    if device is None:
        device = Device(unicode(ua), IBasicDeviceType)
    return device


