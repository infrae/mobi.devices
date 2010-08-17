# package

import os

try:
    # Python 2.6
    import json
except ImportError:
    import simplejson as json

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PLATFORMS = json.load(
    open(os.path.join(DATA_DIR, 'MIT', 'platforms.json'), 'r'))

