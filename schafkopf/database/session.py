import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


class Sessions:

    @staticmethod
    def get_session():
        DATABASE_URL = os.environ['DATABASE_URL']
        engine = create_engine(DATABASE_URL, pool_size=1, max_overflow=0, poolclass=QueuePool)
        my_session = sessionmaker(bind=engine)
        return my_session()
