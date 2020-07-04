import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schafkopf.database.data_model import Punkteconfig
from schafkopf.database.queries import insert_runde, get_punkteconfig_by_name
from schafkopf.scripts.backup_database import backup_database
from schafkopf.scripts.create_empty_database import create_empty_database

logging.getLogger().setLevel(logging.INFO)


def runde_einrichten():
    runden = [
        ('Elternrunde', 'Kalchreuth'),
        ('Profirunde', 'Nürnberg'),
    ]

    path_to_database = '../schafkopf.db'
    if not os.path.isfile(path_to_database):
        create_empty_database()
    else:
        backup_database()
    engine = create_engine('sqlite:///../schafkopf.db')
    session = sessionmaker(bind=engine)()

    punkteconfig = get_punkteconfig_by_name(name='sauspiel_config_plus_hochzeit', session=session)
    if punkteconfig is None:
        punkteconfig = Punkteconfig()
        session.add(punkteconfig)
        session.commit()
        logging.info(f'Punktekonfiguration "{punkteconfig.name}" successfully created')

    inserted = [insert_runde(name=r[0], ort=r[1], punkteconfig_id=punkteconfig.id, session=session) for r in runden]
    session.commit()
    [logging.info(f'Runde "{t.name}" in "{t.ort}" successfully created') for t in inserted]
    session.close()


if __name__ == '__main__':
    runde_einrichten()
