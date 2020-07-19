import datetime
import logging
import os
from shutil import copyfile

logging.getLogger().setLevel(logging.INFO)


def backup_database():
    backup = f'schafkopf_{datetime.datetime.now()}.db'
    current_database = 'schafkopf.db'
    path_to_database = f'schafkopf/{current_database}'
    if os.path.isfile(path_to_database):
        copyfile(path_to_database, f'schafkopf/databases/{backup}')
        logging.info(f'Current database {current_database} backuped successfully as {backup}')


if __name__ == "__main__":
    backup_database()
