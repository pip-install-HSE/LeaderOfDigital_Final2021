import datetime
import psycopg2
from sqlalchemy.engine import Inspector
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer,Float,  String, MetaData, ForeignKey, Boolean, Text, Date, DateTime, create_engine, \
    CheckConstraint
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry as gm
from sqlalchemy.types import TIMESTAMP

from dotenv import load_dotenv
load_dotenv()

from new_database import *

engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}',
                       echo=True)

Session = sessionmaker(bind=engine)  # bound session
session = Session()
session.execute('create extension if not exists postgis')

o = Oil_spill('POLYGON((0 0,1 0,1 1,0 1,0 0))')
s = Settings(0.1, 1, "2019-04-02 14:21:33.715782")
l = Log(datetime.datetime.now(), datetime.datetime.now())
t = Task('POLYGON((0 0,1 0,1 1,0 1,0 0))', 1, datetime.datetime.now(), 0.5, 0.5)
r = Research()
rt = Research_tag("Test")
ob = Object("Test", 'POLYGON((0 0,1 0,1 1,0 1,0 0))')

Base.metadata.create_all(engine, checkfirst=True)

session.add(o)
session.add(s)
session.add(l)
session.add(t)
session.add(r)
session.add(rt)
session.add(ob)
session.flush()
session.commit()
res = session.execute('SELECT * FROM "Oil_spill"')
for i in res.fetchall():
    print(i)

print()
res = session.execute('SELECT * FROM "Log"')
for i in res.fetchall():
    print(i)




