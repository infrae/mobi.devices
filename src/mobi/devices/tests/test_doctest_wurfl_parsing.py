# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
"""
We will start by initializing the database from wurfl stream.
It should return a tuple (db, index)

    >>> from mobi.devices.index.radixtree import NOTSET
    >>> from mobi.devices.wurfl.db import initialize_db
    >>> db, index = initialize_db(config)
    >>> db is not None
    True
    >>> index #doctest: +ELLIPSIS
    <mobi.devices.index.radixtree.RadixTree ...>

Now we'll have a look at what's inside the index.

    >>> user_agent = 'Mozilla/5.0 (iPhone; ...'
    >>> node, string, pos = index.search(user_agent)
    >>> node.value
    <class 'mobi.devices.index.radixtree.NOTSET'>
    >>> string
    u'Mozilla/5.0 (iPhone; '
    >>> pos
    21
    >>> dev_id = node.values().next()


Let's look that up into the database.

    >>> from mobi.devices.wurfl.db import Device
    >>> device = Device.deserialize(db[dev_id])
    >>> device #doctest: +ELLIPSIS
    <mobi.devices.wurfl.parser.Device user_agent="Mozilla/5.0 (iPhone; ...
    >>> int(device.get_capability('xhtml_support_level'))
    4
    >>> device.parent_id
    u'apple_iphone_ver2'
    >>> device.type
    <InterfaceClass mobi.interfaces.devices.IAdvancedDeviceType>
    >>> device.platform
    u'iphone'
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
