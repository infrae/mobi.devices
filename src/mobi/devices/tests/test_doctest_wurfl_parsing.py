"""
We will start by initializing the database from wurfl stream.
It should return a tuple (db, index)

    >>> from mobi.devices.wurfl.db import initialize_db
    >>> db, index = initialize_db(config)
    >>> db #doctest: +ELLIPSIS
    <mobi.devices.index.tcdbm.TCDBMWrapper ...>
    >>> index #doctest: +ELLIPSIS
    <mobi.devices.index.suffixtree.Node ...>

Now we'll have a look at what's inside the index.

    >>> user_agent = 'Mozilla/5.0 (iPhone; ...'
    >>> dev_id = index.search(user_agent).value
    >>> dev_id
    u'apple_generic'

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

"""

import shutil
import os

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

