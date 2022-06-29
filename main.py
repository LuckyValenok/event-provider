from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import DBSession

from data import config

engine = create_engine(f'sqlite:///{config.DATABASE_NAME}', echo=True)
session_factory = sessionmaker(bind=engine)
db_session = DBSession(session_factory())
