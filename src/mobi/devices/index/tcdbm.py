"""
anydbm wrapper for Tokyo Cabinet.
The implementation is partial, only what's needed for our need as been
implemented (get/set).
"""

import pytc as tc

error = tc.Error
library = 'Tokyo cabinet'

def open(filename, flag='r', mode=0666):
    # XXX: implement mode
    rfilename = filename + '.tch'
    tcflags = 0
    if 'c' == flag:
        tcflags = tc.HDBOCREAT | tc.HDBOWRITER
    elif 'w' == flag:
        tcflags = tc.HDBOWRITER
    elif 'r' == flag:
        tcflags = tc.HDBOREADER
    elif 'n' == flag:
        tcflags = tc.HDBOTRUNC | tc.HDBOCREAT | tc.HDBOWRITER

    try:
        db = TCDBMWrapper()
        db.open(rfilename, tcflags)
        return db
    except tc.Error, e:
        raise


class TCDBMWrapper(tc.HDB):

    def get(self, key, default=None):
        try:
            return super(TCDBMWrapper, self).get(key)
        except KeyError:
            return default

    def __getitem__(self, key):
        return super(TCDBMWrapper, self).get(key)

    def __setitem__(self, key, value):
        return self.put(key, value)
