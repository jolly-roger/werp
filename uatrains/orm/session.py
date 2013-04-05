from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import sched
import time
import datetime


null_engine = create_engine('postgresql://uatrains:v2T<%tNp@localhost:5432/uatrains', poolclass=NullPool)
q_engine = create_engine('postgresql://uatrains:v2T<%tNp@localhost:5432/uatrains', pool_size=1024, max_overflow=0,
	pool_recycle=3600)
sescls = sessionmaker()
ses = sessionmaker(bind=q_engine)