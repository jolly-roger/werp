from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


null_engine = create_engine('postgresql://werp:0v}II587@localhost:5432/werp', poolclass=NullPool)
q_engine = create_engine('postgresql://werp:0v}II587@localhost:5432/werp', pool_size=1024, max_overflow=0,
	pool_recycle=3600)
sescls = sessionmaker()
ses = sessionmaker(bind=q_engine)