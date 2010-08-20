"""
We will start by initializing the database from wurfl stream.
It should return a tuple (db, index)

    >>> from mobi.devices.wurfl.db import initialize_db
    >>> db, index = initialize_db(config)
    >>> db #doctest: +ELLIPSIS
    <mobi.devices.index.tcdbm.TCDBMWrapper ...>
    >>> index #doctest: +ELLIPSIS
    <mobi.devices.index.suffixtree.SuffixTree ...>

Now we'll have a look at what's inside the index.

    >>> user_agent = 'Mozilla/5.0 (iPhone; ...'
    >>> node, string, pos = index.search(user_agent)
    >>> dev_id = node.value
    >>> dev_id
    u'apple_generic'
    >>> string
    u'Mozilla/5.0 (iPhone;'
    >>> pos
    19

Let's look that up into the database.

    >>> from mobi.devices.wurfl.db import Device
    >>> device = Device.deserialize(db[dev_id])
    >>> device
    <mobi.devices.wurfl.parser.Device user_agent="Mozilla/5.0 (iPhone;">
    >>> int(device.get_capability('xhtml_support_level'))
    4
    >>> device.parent_id
    u'generic_xhtml'
    >>> device.type
    <InterfaceClass mobi.interfaces.devices.IAdvancedDeviceType>
    >>> device.platform
    u'iphone'

Let's play a bit more with the index.

    >>> from mobi.devices.index.suffixtree import WildcardSearch
    >>> search = WildcardSearch(index)
    >>> firefox_ua = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5;" \\
    ...     " en-US; rv:1.9.1.8) Gecko/20100202 Firefox/3.5.8"
    >>> results = search(firefox_ua)
    >>> res = results[0][0]
    >>> results
    >>> device = Device.deserialize(db[res.value])
    >>> device.id
    ''
    >>> device.platform
    'ads'
    >>> device.get_capability('is_wireless_device')
    u'false'
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
        #shutil.rmtree(data_dir)
    except:
        pass

def test_suite():
    import unittest
    import doctest

    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite(__name__, setUp=setup, tearDown=teardown))
    return suite
