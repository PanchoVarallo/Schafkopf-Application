import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from schafkopf.utils.settings_utils import get_db, get_database_url, Database


class Sessions:
    if "DATABASE_URL" in os.environ:
        # On Heroku Server for production environment
        engine = create_engine(os.environ['DATABASE_URL'], poolclass=QueuePool, pool_size=15, max_overflow=0)
    else:
        if get_db() == Database.SQLITE:
            # Using sqlite
            engine = create_engine(get_database_url(), poolclass=NullPool)
        elif get_db() == Database.POSTGRES:
            # Using the Heroku postgres database locally
            # This is the explanation on Heroku, but it die not work for me
            # engine = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
            # This works if we add a +psycopg2 to the database url
            engine = create_engine(get_database_url())
        else:
            raise ValueError

    @staticmethod
    def get_engine():
        return Sessions.engine

    @staticmethod
    def get_session():
        my_session = sessionmaker(bind=Sessions.engine)
        return my_session()
