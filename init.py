import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schafkopf.database.data_model import Base
from schafkopf.database.data_model import Punkteconfig
from schafkopf.database.queries import insert_runde, get_punkteconfig_by_name, insert_teilnehmer
from schafkopf.scripts.backup_database import backup_database

logging.getLogger().setLevel(logging.INFO)


def database_init():
    runden = [
        ('Sonntagsrunde', 'Kalchreuth'),
    ]
    teilnehmers = [
        # ("Johannes", "Holzwarth"),
        # ("Ted", "Harder"),
        # ("Marcus", "Becher"),
        # ("Michael", "Theil"),
        ("Mathias", "Sirvent"),
        ("Mariana", "Sirvent"),
        ("Maria", "Schütz"),
        ("Ricardo", "Sirvent"),
    ]

    path_to_database = 'schafkopf/schafkopf.db'
    if not os.path.isfile(path_to_database):
        create_empty_database()
    else:
        backup_database()
    engine = create_engine('sqlite:///schafkopf/schafkopf.db')
    if len(runden) > 0:
        session = sessionmaker(bind=engine)()
        punkteconfig = get_punkteconfig_by_name(name='sauspiel_config_plus_hochzeit', session=session)
        if punkteconfig is None:
            punkteconfig = Punkteconfig()
            session.add(punkteconfig)
            session.commit()
            # logging.info(f'Punktekonfiguration "{punkteconfig.name}" successfully created')
        inserted = [insert_runde(name=r[0], ort=r[1], punkteconfig_id=punkteconfig.id, session=session) for r in runden]
        session.commit()
        [logging.info(f'Runde "{t.name}" in "{t.ort}" successfully created') for t in inserted]
        session.close()

    if len(teilnehmers) > 0:
        engine = create_engine("sqlite:///schafkopf/schafkopf.db")
        session = sessionmaker(bind=engine)()
        inserted = [insert_teilnehmer(vorname=t[0], nachname=t[1], session=session) for t in teilnehmers]
        session.commit()
        [logging.info(f'Teilnehmer "{t.name}" successfully created') for t in inserted]
        session.close()


def create_empty_database():
    backup_database()
    database = 'schafkopf.db'
    engine = create_engine(f'sqlite:///schafkopf/{database}')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logging.info(f'Empty database {database} created successfully')


if __name__ == '__main__':
    database_init()
