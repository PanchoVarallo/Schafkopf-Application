from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Sessions:

    @staticmethod
    def get_session():
        engine = create_engine("sqlite:///schafkopf/schafkopf.db")
        my_session = sessionmaker(bind=engine)
        return my_session()
