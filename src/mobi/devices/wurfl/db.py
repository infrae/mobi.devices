# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
from xml.sax import make_parser
from mobi.devices.wurfl.parser import Device, WURFLContentHandler
from mobi.devices.index.radixtree import RadixTree
from mutex import mutex
import pickle
import gzip
import logging
import os
logger = logging.getLogger('mobi.devices')

db_mutex = mutex()


try:
    # use tokyo cabinet except on windows
    import mobi.devices.index.tcdbm as dbm
    logger.info('tcdbm found.')
except ImportError:
    # non posix platfroms
    try:
        logger.info('tokyo cabinet dbm not found try with dbm.')
        import dbm
        logger.info('dbm found.')
    except ImportError:
        logger.info('dbm not found import anydbm')
        import dbm


_dirname = os.path.dirname(__file__)

DEFAULTS = {
    'var': '/tmp',
    'wurfl_file': os.path.join(
        _dirname, '..', 'data', 'WURFL', 'wurfl.xml.gz'),
}

def initialize_db(config=None):
    local_config = DEFAULTS.copy()
    if config is not None:
        local_config.update(config)
    if not local_config.has_key('var'):
        raise ValueError('no storage directory ("var"), defined')
    dbfilename = os.path.join(local_config['var'], 'devices')
    return open_or_create(dbfilename, local_config['wurfl_file'])

def open_or_create(filename, wurfl_file):

    def open_db(mode):
        db = dbm.open(filename, mode)
        Device.db = db
        return db

    try:
        db = open_db('r')
    except:
        logger.info('db does not exists, create it at %s' % filename)
        # open and trunk it
        db = open_db('n')
        try:
            if not wurfl_file or not os.path.exists(wurfl_file):
                raise ValueError("wurfl file does not exists: '%s'" %
                                 wurfl_file)
            open_file = open
            if wurfl_file.endswith('.gz'):
                open_file = gzip.open
            f = open_file(wurfl_file, 'r')
            try:
                logger.info('creating device index...')
                st = build_index_tree(db, f)
                logger.info('storing device index...')
                db['__radixtree__'] = pickle.dumps(st)
            finally:
                f.close()
        finally:
            db.close()
        # reopen database in readonly
        db = open_db('r')
    return db, pickle.loads(db['__radixtree__'])


def build_index_tree(db, wurfl_xml_stream):
    parser = make_parser()
    st = RadixTree()
    ch = WURFLContentHandler(db, st)
    parser.setContentHandler(ch)
    parser.parse(wurfl_xml_stream)
    return st
