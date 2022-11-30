import csv
import enum
import urllib

from sqlalchemy import (Column, Enum, Integer, MetaData, String, Table,
                        create_engine, false)

from util.constants import ID_MAPPING as idMapping
from sqlalchemy.orm import declarative_base

import settings
from db_connection import Session

Base = declarative_base()

class ItemType(enum.Enum):
    weapon = "weapon"
    armor = "armor"

class Honing(Base):
    __tablename__ = "Honings"
    id = Column(Integer, primary_key=True)
    discordId = Column(String, nullable=False)
    discordUsername = Column(String, nullable=False)
    tierBaseItemLevel = Column(Integer, nullable=False)
    itemType = Column(Enum(ItemType))
    numberOfTaps = Column(Integer, nullable=False)
    outputLevel = Column(Integer, nullable=False)
    goldUsedFromAvg = Column(Integer, nullable=False)
    shardsUsedFromAvg = Column(Integer, nullable=False)
    leapstonesUsedFromAvg = Column(Integer, nullable=False)
    redStonesUsedFromAvg = Column(Integer, default=0, nullable=False)
    blueStonesUsedFromAvg = Column(Integer, default=0, nullable=False)
    fusionsUsedFromAvg = Column(Integer, nullable=False)
    description = Column(String, nullable=False)


## Scripts used to create the table and populate data
## Currently not being used   
def createTable():
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
    
    meta =  MetaData()
    honings = Table(
        "Honings", meta,
        Column("id", Integer, primary_key=True),
        Column("discordId", String, nullable=False),
        Column("discordUsername", String, nullable=False),
        Column("tierBaseItemLevel", Integer, nullable=False),
        Column("itemType", Enum(ItemType), nullable=False),
        Column("numberOfTaps", Integer, nullable=False),
        Column("outputLevel", Integer, nullable=False),
        Column("goldUsedFromAvg", Integer, nullable=False),
        Column("shardsUsedFromAvg", Integer, nullable=False),
        Column("leapstonesUsedFromAvg", Integer, nullable=False),
        Column("redStonesUsedFromAvg", Integer, nullable=False),
        Column("blueStonesUsedFromAvg", Integer, nullable=False),
        Column("fusionsUsedFromAvg", Integer, nullable=False),
        Column("description", String, nullable=True)
    )
    
    meta.create_all(engine)
    
def uploadData():
    with Session() as sess:
        with open('dataEntry.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader,None)
            for row in reader:
                discordId = int(row[0])
                discordUsername = idMapping[int(discordId)]
                tierBaseItemLevel = int(row[1])
                itemType = str(row[2])
                numberOfTaps = int(row[3])
                outputLevel = int(row[4])
                goldUsedFromAvg = int(row[5])
                shardsUsedFromAvg = int(row[6])
                leapstonesUsedFromAvg = int(row[7])
                redStonesUsedFromAvg = int(row[8])
                blueStonesUsedFromAvg = int(row[9])
                fusionsUsedFromAvg = int(row[10])
                try:
                    description = str(row[11])
                except:
                    description = "on unknown character"
                newHone = Honing(
                    discordId=discordId,
                    discordUsername=discordUsername,
                    tierBaseItemLevel=tierBaseItemLevel,
                    itemType=itemType,
                    numberOfTaps=numberOfTaps,
                    outputLevel=outputLevel,
                    goldUsedFromAvg=goldUsedFromAvg,
                    shardsUsedFromAvg=shardsUsedFromAvg,
                    leapstonesUsedFromAvg=leapstonesUsedFromAvg,
                    redStonesUsedFromAvg=redStonesUsedFromAvg,
                    blueStonesUsedFromAvg=blueStonesUsedFromAvg,
                    fusionsUsedFromAvg=fusionsUsedFromAvg,
                    description=description
                )
                sess.add(newHone)
                sess.commit()