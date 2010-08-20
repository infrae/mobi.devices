"""
    This module helps to find out what kind of mobile device the request is
    issued from.

    >>> from mobi.devices.classifiers import get_device

    >>> ua = "Mozilla/5.0 (SymbianOS/9.1; U; [en]; Series60/3.0" \\
    ...     " NokiaE60/4.06.0) AppleWebKit/413 (KHTML, like Gecko) Safari/413"
    >>> device = get_device(ua)
    >>> device # doctest: +ELLIPSIS
    <mobi.devices.device.MITDevice ...>
    >>> device.type
    <InterfaceClass mobi.interfaces.devices.IBasicDeviceType>
    >>> device.platform
    u'symbian'

    Let's check the Wurfl classifier with computer devices.

    >>> from mobi.devices.classifiers import WurflClassifier
    >>> firefox_ua = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5;" \\
    ...     " en-US; rv:1.9.1.8) Gecko/20100202 Firefox/3.5.8"
    >>> wclassifier = WurflClassifier(config)
    >>> device = wclassifier(firefox_ua)
    >>> device  # doctest: +ELLIPSIS
    <mobi.devices.device.WDevice ...>
    >>> device.platform
    u'computer'

    Let's try with Google spider boot user agent. We would expect spider
    platform but it's computer... :

    >>> google_ua = "Mozilla/5.0 (compatible; Googlebot/2.1;" \\
    ...     " +http://www.google.com/bot.html)"
    >>> device = wclassifier(google_ua)
    >>> device.platform
    u'computer'

"""

import shutil
import os
from mobi.devices.wurfl.parser import Device

data_dir = os.path.join(os.path.dirname(__file__), 'var')
config = {
    'var': data_dir
}

def setup(test):
    teardown(test)
    try:
        os.mkdir(data_dir)
    except OSError:
        pass

def teardown(test):
    try:
        if Device.db:
            Device.db.close()
        shutil.rmtree(data_dir)
    except:
        pass

def test_suite():
    import unittest
    import doctest

    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite(__name__, setUp=setup, tearDown=teardown))
    return suite
