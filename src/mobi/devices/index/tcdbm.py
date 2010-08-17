import pytc as tc
import os

error = tc.Error
library = 'Tokyo cabinet'

def open(filename, flag='r', mode=0666):
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

    def __delitem__(self, key):
        return self.out(key)

    def __contains__(self, key):
        return self.has_key(key)

    def has_key(self, key):
        return bool(self.get(key, False))

    def __getitem__(self, key):
        return super(TCDBMWrapper, self).get(key)

    def __setitem__(self, key, value):
        return self.put(key, value)

