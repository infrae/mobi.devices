import json
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy import select
from os import path


DB_URI = 'mysql://root@127.0.0.1:3306/mobi_service'
engine = create_engine(DB_URI, echo=False)


metadata = MetaData(engine)
whitelist_table = Table('mobi_service_whitelist', metadata,
    Column('pattern', String(127)),
    Column('pagetype', String(15)),
    Column('platform', String(15)),
    Column('certs', Integer(1)),
    Column('description', String(255))
)
platform_table = Table('mobi_service_platform', metadata,
    Column('platform', String(15)),
    Column('description', String(63)))


connection = engine.connect()
infos = connection.execute(select([whitelist_table])).fetchall()
device_infos = []
platforms = {}

for pattern, device_type, platform, certs, description in infos:
    d = {
        'pattern': pattern,
        'device_type': device_type,
        'platform': platform,
        'certs': certs,
        'description': description,
    }
    device_infos.append(d)

infos = connection.execute(select([platform_table])).fetchall()

for platform, description in infos:
    platforms[platform] = description

export_dir = path.join(path.dirname(__file__), '..', 'data', 'MIT')

export_file = path.join(export_dir, 'device_user_agent_patterns.json')
platform_file = path.join(export_dir, 'platforms.json')

with open(export_file, 'w') as fd:
    json.dump(device_infos, fd, indent=4)

with open(platform_file, 'w') as fd:
    json.dump(platforms, fd, indent=4)
