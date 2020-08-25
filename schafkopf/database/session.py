import os

from sqlalchemy import create_engine
import psycopg2
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool


class Sessions:
    # Using the Heroku postgres database locally
    # engine = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    # For sqlite
    engine = create_engine(os.environ['DATABASE_URL'], poolclass=NullPool)

    # On Heroku Server
    # engine = create_engine(os.environ['DATABASE_URL'], poolclass=QueuePool, pool_size=15, max_overflow=0)

    @staticmethod
    def get_session():
        my_session = sessionmaker(bind=Sessions.engine)
        return my_session()
