from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


q_engine = create_engine('postgresql://log:0v}II587@localhost:5432/log', pool_size=1024, max_overflow=0,
	pool_recycle=3600)
sescls = sessionmaker()
ses = sessionmaker(bind=q_engine)