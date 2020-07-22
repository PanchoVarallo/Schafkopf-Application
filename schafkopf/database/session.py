import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


class Sessions:
    engine = create_engine(os.environ['DATABASE_URL'])

    @staticmethod
    def get_session():
        my_session = sessionmaker(bind=Sessions.engine)
        return my_session()
