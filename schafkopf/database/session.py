import os

from sqlalchemy import create_engine
import psycopg2
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool


class Sessions:
    # engine = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    engine = create_engine(os.environ['DATABASE_URL'], poolclass=QueuePool)

    @staticmethod
    def get_session():
        my_session = sessionmaker(bind=Sessions.engine)
        return my_session()
