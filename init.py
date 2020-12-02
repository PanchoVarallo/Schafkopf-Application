import logging

from schafkopf.database.data_model import Base
from schafkopf.database.queries import insert_default_punkteconfig, insert_user
from schafkopf.database.session import Sessions
from schafkopf.utils.settings_utils import get_database_url, get_init_username, get_init_password

logging.getLogger().setLevel(logging.INFO)


def database_init():
    engine = Sessions.get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # Note: here you can change the default configuration of points (currently: 50-20-10)
    insert_default_punkteconfig()
    insert_user(username=get_init_username(), password=get_init_password())
    logging.info(f'Database in {get_database_url()} created successfully')


if __name__ == '__main__':
    database_init()
