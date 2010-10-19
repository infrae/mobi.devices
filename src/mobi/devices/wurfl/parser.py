# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
from xml.sax.handler import ContentHandler
from zope.interface import implements
from mobi.interfaces.devices import (IDevice,
    IBasicDeviceType, IStandardDeviceType, IAdvancedDeviceType)
from mobi.devices.wurfl.platforms import PLATFORMS
import cPickle as pickle


class Device(object):
    """ A wurfl device object
    """
    implements(IDevice)
    db = None

    # parent resolve method
    @staticmethod
    def resolve(x):
        data = Device.db.get(x)
        if data:
            return Device.deserialize(data)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)

    def __init__(self, id, user_agent, parent_id=None, caps=None):
        self.id = id
        self.parent_id = parent_id
        self.user_agent = user_agent
        self.capabilities = caps or {}

    @property
    def parent(self):
        if hasattr(self, '__parent'):
            return self.__parent
        self.__parent = self.resolve(self.parent_id)
        return self.__parent

    def serialize(self):
        if hasattr(self, '__parent'):
            del self.__parent
        if hasattr(self, '__type'):
            del self.__type
        if hasattr(self, '__platform'):
            del self.__platform
        return pickle.dumps(self)

    @property
    def platform(self):
        if hasattr(self, '__platform'):
            return self.__platform

        for exstring in [u'bot', u'spider', u'crawl']:
            if exstring in self.user_agent:
                self.__platform = u'spider'
                return self.__platform

        if self.get_capability('is_wireless_device') == u'true':
            platform_names = PLATFORMS.keys()
            os = str(self.get_capability('device_os')).lower()
            if os:
                for name in platform_names:
                    if name in os:
                        self.__platform = name
                        return self.__platform
            self.__platform = u'featurephone'
        else:
            fallbacks = self._fallback_device_ids()
            for fallback in fallbacks:
                if 'bot' in fallback or \
                        fallback == 'generic_web_crawler':
                    self.__platform = u'spider'
                    return self.__platform
            self.__platform = u'computer'
        return self.__platform

    def _fallback_device_ids(self):
        ids = []
        current_device = self
        while current_device.parent:
            ids.append(current_device.parent.id)
            current_device = current_device.parent
        return ids

    @property
    def type(self):
        if hasattr(self, '__type'):
            return self.__type
        try:
            support_level = int(self.get_capability('xhtml_support_level'))
            if support_level >= 4:
                self.__type = IAdvancedDeviceType
            elif support_level == 3:
                self.__type = IStandardDeviceType
            else:
                self.__type = IBasicDeviceType
            return self.__type
        except (ValueError, TypeError):
            self.__type = IBasicDeviceType
            return self.__type

    def get_capability(self, name):
        if name in self.capabilities:
            return self.capabilities[name]
        if self.parent:
            return self.parent.get_capability(name)
        return None

    def __repr__(self):
        return '<%s.Device user_agent="%s">' % (__name__, self.user_agent)


class WURFLContentHandler(ContentHandler):

    def __init__(self, db, suffix_tree):
        self.db = db
        self.devices = []
        self.suffix_tree = suffix_tree

    def reset(self):
        self.device = None

    def startDocument(self):
        self.reset()

    def endDocument(self):
        self.reset()

    def startElement(self, element, attributes):
        attrs = attributes.copy()
        if element == 'device':
            self.device = self._build_device(element, attrs)
        if element == 'capability' and self.device:
            self.device.capabilities[attrs['name']] = attrs['value']

    def endElement(self, element):
        if element == 'device':
            self.db[self.device.id] = self.device.serialize()
            if self.device.user_agent:
                self.suffix_tree.add(self.device.user_agent,
                                     value=self.device.id)
            self.devices.append(self.device)
            self.device = None

    def _build_device(self, element, attrs):
        device = Device(attrs['id'], attrs['user_agent'],
                        parent_id=attrs['fall_back'])
        return device
