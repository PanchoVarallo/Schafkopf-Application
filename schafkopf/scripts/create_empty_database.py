import logging

from sqlalchemy import create_engine

from schafkopf.database.data_model import Base
from schafkopf.scripts.backup_database import backup_database

logging.getLogger().setLevel(logging.INFO)


def create_empty_database():
    backup_database()
    database = 'schafkopf.db'
    engine = create_engine(f'sqlite:///../{database}')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logging.info(f'Empty database {database} created successfully')


if __name__ == '__main__':
    create_empty_database()
