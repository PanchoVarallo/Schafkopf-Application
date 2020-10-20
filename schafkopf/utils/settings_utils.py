import configparser
import enum

ini = 'settings.ini'


class Database(enum.Enum):
    SQLITE = 1
    POSTGRES = 2


def get_db() -> Database:
    return Database[get_entry('Database', 'db')]


def get_database_url() -> str:
    return get_entry('Database', 'database_url')


def get_init_username() -> str:
    return get_entry('Auth', 'username')


def get_init_password() -> str:
    return get_entry('Auth', 'password')


def get_entry(section: str, entry: str) -> str:
    config = _get_settings_ini_config()
    if section not in config:
        raise ValueError(f'Ini is not valid. "{section}" section is missing.')
    if entry not in config[section]:
        raise ValueError(f'Ini is not valid. {entry} entry for section {section} is missing.')
    return config[section][entry]


def _get_settings_ini_config():
    config = configparser.ConfigParser()
    config.read(ini)
    return config
