"""
    This module helps to find out what kind of mobile device the request is
    issued from.

    >>> from playmobile.devices.classifiers import get_device

    >>> ua = "Mozilla/5.0 (SymbianOS/9.1; U; [en]; Series60/3.0" \\
    ...     " NokiaE60/4.06.0) AppleWebKit/413 (KHTML, like Gecko) Safari/413"
    >>> device = get_device(ua)
    >>> device # doctest: +ELLIPSIS
    <playmobile.devices.device.MITDevice ...>
    >>> device.get_type()
    <InterfaceClass playmobile.interfaces.devices.IBasicDeviceType>
    >>> device.get_platform()
    u'symbian'

    Let's check the Wurfl classifier with computer devices.

    >>> from playmobile.devices.classifiers import WurflClassifier
    >>> firefox_ua = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5;" \\
    ...     " en-US; rv:1.9.1.8) Gecko/20100202 Firefox/3.5.8"
    >>> wclassifier = WurflClassifier()
    >>> device = wclassifier(firefox_ua)
    >>> device  # doctest: +ELLIPSIS
    <playmobile.devices.device.WDevice ...>
    >>> device.get_platform()
    u'computer'

    Let's try with Google spider boot user agent. We would expect spider
    platform but it's computer... :/

    >>> google_ua = "Mozilla/5.0 (compatible; Googlebot/2.1;" \\
    ...     " +http://www.google.com/bot.html)"
    >>> device = wclassifier(google_ua)
    >>> device.get_platform()
    u'computer'

"""
