import urllib

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import settings

server = settings.SERVER
database = settings.DATABASE
username = settings.USERNAME
password = settings.PASSWORD   
driver= settings.DRIVER
params = urllib.parse.quote_plus(
    'Driver=%s;' % driver +
    'Server=tcp:%s,1433;' % server +
    'Database=%s;' % database +
    'Uid=%s;' % username +
    'Pwd={%s};' % password +
    'Encrypt=yes;' +
    'TrustServerCertificate=no;' +
    'Connection Timeout=30;'
    )
conn_str = "mssql+pyodbc:///?odbc_connect=" + params

engine = create_engine(conn_str, pool_size=5, pool_recycle=3600)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)