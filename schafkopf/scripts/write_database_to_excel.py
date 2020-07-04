import logging
import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schafkopf.database.queries import get_runden, get_teilnehmer, get_punkteconfigs, get_einzelspiele, \
    get_verdopplungen, get_resultate
from schafkopf.scripts.backup_database import backup_database

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

logging.getLogger().setLevel(logging.INFO)


def write_database_to_excel():
    backup_database()
    engine = create_engine("sqlite:///../schafkopf.db")
    session = sessionmaker(bind=engine)()
    runden_df = get_runden(dataframe=True, session=session)
    teilnehmers_df = get_teilnehmer(dataframe=True, session=session)
    punkteconfigs_df = get_punkteconfigs(dataframe=True, session=session)
    einzelspiele_df = get_einzelspiele(dataframe=True, session=session)
    resultate_df = get_resultate(dataframe=True, session=session)
    verdopplungen_df = get_verdopplungen(dataframe=True, session=session)
    xlsx = f'schafkopf_{datetime.datetime.now()}.xlsx'
    with pd.ExcelWriter(f'../databases/{xlsx}') as writer:
        runden_df.to_excel(writer, sheet_name='runden', index=False)
        teilnehmers_df.to_excel(writer, sheet_name='teilnehmer', index=False)
        punkteconfigs_df.to_excel(writer, sheet_name='punkteconfigs', index=False)
        einzelspiele_df.to_excel(writer, sheet_name='einzelspiele', index=False)
        resultate_df.to_excel(writer, sheet_name='resultate', index=False)
        verdopplungen_df.to_excel(writer, sheet_name='verdopplungen', index=False)
    logging.info(f'All database entries written to {xlsx}')
    session.close()


if __name__ == "__main__":
    write_database_to_excel()
