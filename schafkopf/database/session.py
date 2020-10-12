import os

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool


class Sessions:
    engine = create_engine(os.environ['DATABASE_URL'], poolclass=QueuePool, pool_size=15, max_overflow=0)
    # if os.environ['ENVIRONMENT'] is None:
    #     # On Heroku Server
    # elif os.environ['ENVIRONMENT'] == 'SQLITE_DATABASE':
    #     # Using sqlite
    #     engine = create_engine(os.environ['DATABASE_URL'], poolclass=NullPool)
    # elif os.environ['ENVIRONMENT'] == 'HEROKU_DATABASE':
    #     # Using the Heroku postgres database locally
    #     engine = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    @staticmethod
    def get_session():
        my_session = sessionmaker(bind=Sessions.engine)
        return my_session()
