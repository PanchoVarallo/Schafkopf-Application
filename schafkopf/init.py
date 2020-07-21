import json
import logging
import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schafkopf.database.data_model import Base
from schafkopf.database.data_model import Punkteconfig
from schafkopf.database.queries import insert_runde, get_punkteconfig_by_name, insert_teilnehmer

logging.getLogger().setLevel(logging.INFO)


def database_init():
    with open('init.json') as json_file:
        data = json.load(json_file)
        runden = data['Runden']
        teilnehmers = data['Teilnehmer']

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

        inserted = [insert_runde(datum=datetime.strptime(r['datum'], '%Y-%m-%d'), name=r['name'], ort=r['ort'],
                                 punkteconfig_id=punkteconfig.id, session=session) for r
                    in runden]
        session.commit()
        [logging.info(f'Runde "{t.name}" von "{t.datum}" in "{t.ort}" successfully created') for t in inserted]
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
    database_url = os.environ['DATABASE_URL']
    engine = create_engine(database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logging.info(f'Empty database created successfully')


if __name__ == '__main__':
    create_empty_database()
    database_init()
