# package

import os
try:
    # Python 2.6
    import json
except ImportError:
    import simplejson as json


DATA_DIR = os.path.join(__file__, '..', '..', '..', 'data')
PLATFORMS = json.loads(
    open(os.path.join(DATA_DIR, 'MIT', 'platforms.json'), 'r'))


