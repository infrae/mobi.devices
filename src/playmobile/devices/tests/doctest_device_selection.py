"""
    This module helps to find out what kind of mobile device the request is
    issued from.

    >>> from playmobile.devices.classifiers import get_device

    >>> ua = "Mozilla/5.0 (SymbianOS/9.1; U; [en]; Series60/3.0 NokiaE60/4.06.0) AppleWebKit/413 (KHTML, like Gecko) Safari/413"
    >>> device = get_device(ua)
    >>> device # doctest: +ELLIPSIS
    <playmobile.devices.device.MITDevice ...>
    >>> device.get_type()
    <InterfaceClass playmobile.interfaces.devices.IBasicDeviceType>

    
"""
