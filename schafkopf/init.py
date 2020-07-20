import datetime
import logging
import os
from shutil import copyfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schafkopf.database.data_model import Base
from schafkopf.database.data_model import Punkteconfig
from schafkopf.database.queries import insert_runde, get_punkteconfig_by_name, insert_teilnehmer
import json

logging.getLogger().setLevel(logging.INFO)


def database_init():
    with open('init.json') as json_file:
        data = json.load(json_file)
        runden = data['Runden']
        teilnehmers = data['Teilnehmer']

    path_to_database = 'schafkopf.db'
    if not os.path.isfile(path_to_database):
        create_empty_database()
    else:
        backup_database()
    database_url = os.environ['DATABASE_URL']
    engine = create_engine(database_url)
    if len(runden) > 0:
        session = sessionmaker(bind=engine)()
        punkteconfig = get_punkteconfig_by_name(name='sauspiel_config_plus_hochzeit', session=session)
        if punkteconfig is None:
            punkteconfig = Punkteconfig()
            session.add(punkteconfig)
            session.commit()
            # logging.info(f'Punktekonfiguration "{punkteconfig.name}" successfully created')
        inserted = [insert_runde(name=r['name'], ort=r['ort'], punkteconfig_id=punkteconfig.id, session=session) for r
                    in runden]
        session.commit()
        [logging.info(f'Runde "{t.name}" in "{t.ort}" successfully created') for t in inserted]
        session.close()

    if len(teilnehmers) > 0:
        database_url = os.environ['DATABASE_URL']
        engine = create_engine(database_url)
        session = sessionmaker(bind=engine)()
        inserted = [insert_teilnehmer(vorname=t['vorname'], nachname=t['nachname'], session=session) for t in
                    teilnehmers]
        session.commit()
        [logging.info(f'Teilnehmer "{t.name}" successfully created') for t in inserted]
        session.close()


def create_empty_database():
    backup_database()
    database_url = os.environ['DATABASE_URL']
    engine = create_engine(database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logging.info(f'Empty database created successfully')


def backup_database():
    backup = f'schafkopf_{datetime.datetime.now()}.db'
    current_database = 'schafkopf.db'
    path_to_database = f'{current_database}'
    if os.path.isfile(path_to_database):
        copyfile(path_to_database, f'{backup}')
        logging.info(f'Current database {current_database} backuped successfully as {backup}')


if __name__ == '__main__':
    database_init()
