import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schafkopf.database.queries import insert_teilnehmer
from schafkopf.scripts.backup_database import backup_database
from schafkopf.scripts.create_empty_database import create_empty_database

logging.getLogger().setLevel(logging.INFO)


def teilnehmer_einrichten():
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

    current_database = 'schafkopf.db'
    path_to_database = f'../{current_database}'
    if not os.path.isfile(path_to_database):
        create_empty_database()
    else:
        backup_database()
    engine = create_engine("sqlite:///../schafkopf.db")
    session = sessionmaker(bind=engine)()
    inserted = [insert_teilnehmer(vorname=t[0], nachname=t[1], session=session) for t in teilnehmers]
    session.commit()
    [logging.info(f'Teilnehmer "{t.name}" successfully created') for t in inserted]
    session.close()


if __name__ == "__main__":
    teilnehmer_einrichten()
