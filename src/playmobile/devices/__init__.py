# package

<<<<<<< local
from beaker.cache import CacheManager
=======
import os
try:
    # Python 2.6
    import json
except ImportError:
    import simplejson as json
>>>>>>> other

<<<<<<< local
# replace this cache manager to enable a configured cache
cache = CacheManager(enabled=False,
    cache_regions={'playmobile.devices': {}})
=======

DATA_DIR = os.path.join(__file__, '..', '..', '..', 'data')
PLATFORMS = json.loads(
    open(os.path.join(DATA_DIR, 'MIT', 'platforms.json'), 'r'))


>>>>>>> other
