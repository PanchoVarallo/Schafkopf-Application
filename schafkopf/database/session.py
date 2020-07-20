from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

class Sessions:

    @staticmethod
    def get_session():
        DATABASE_URL = os.environ['DATABASE_URL']
        engine = create_engine(DATABASE_URL)
        my_session = sessionmaker(bind=engine)
        return my_session()
