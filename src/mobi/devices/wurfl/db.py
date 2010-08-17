from xml.sax import make_parser
from mobi.devices.wurfl.parser import Device, WURFLContentHandler
from mobi.devices.index.suffixtree import Node
import pickle
import gzip
import logging
import os
logger = logging.getLogger('mobi.devices')


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
    'var': os.path.join(_dirname, 'data'),
    'wurfl_file': os.path.join(
        _dirname, '..', 'data', 'WURFL', 'wurfl.xml.gz'),
}

def initialize_db(config=None):
    _config = DEFAULTS.copy()
    if _config is not None:
        _config.update(config)
    if not _config.has_key('var'):
        raise ValueError('no storage directory ("var"), defined')
    dbfilename = os.path.join(config['var'], 'devices')
    return open_or_create(dbfilename, _config['wurfl_file'])

def open_or_create(filename, wurfl_file):
    try:
        # first try to open it as readonly
        db = dbm.open(filename, 'r')
        Device.db = db
    except:
        logger.info('db does not exists, create it at %s' % filename)
        # open and trunk it
        db = dbm.open(filename, 'n')
        Device.db = db
        try:
            if not os.path.exists(wurfl_file):
                raise ValueError('wurfl file does not exists: %s' %
                                 wurfl_file)
            open_file = open
            if wurfl_file.endswith('.gz'):
                open_file = gzip.open
            f = open_file(wurfl_file, 'r')
            try:
                logger.info('creating device index...')
                st = build_index_tree(db, f)
                logger.info('storing device index...')
                db['__suffixtree__'] = pickle.dumps(st)
            finally:
                f.close()
        finally:
            db.close()
        # reopen database in readonly
        db = dbm.open(filename, 'r')
        Device.db = db
    return db, pickle.loads(db['__suffixtree__'])


def build_index_tree(db, wurfl_xml_stream):
    parser = make_parser()
    st = Node('Root')
    ch = WURFLContentHandler(db, st)
    parser.setContentHandler(ch)
    parser.parse(wurfl_xml_stream)
    return st
