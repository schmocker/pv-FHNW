from dotenv import load_dotenv
from os import environ
import os

# load env from .env file
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print(ROOT_DIR)


class Config(object):
    ENV = True
    LOGGING_LEVEL = int(environ.get('LOGGING_LEVEL', default=5))
    LOGGING_FORMATTER = environ.get('LOGGING_FORMATTER', default='%(levelname)s::%(module)s: %(message)s')
    SECRET_KEY = environ.get('SECRET_KEY', default='8"79cpvp?xyCBPZV]T8~-m3"*0x>dm88Nm$PV]sW}AMq/Fj4zBa%fGt~Xa>emVw')
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', default=False) in [True, 'True']
    # SQLALCHEMY_USE_FLASK = environ.get('SQLALCHEMY_USE_FLASK', default=False) in [True, 'True', 'true']

    # DATABASE
    DB_NAME = environ.get('DB_NAME', default="database")
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(ROOT_DIR,"temp",DB_NAME)}.db'


class ConfigMigrated(object):
    # TODO: Extend with MySQL
    # DATABASE
    DB_NAME = environ.get('DB_NAME', default="database")
    SQLALCHEMY_DATABASE_URI = f'mysql:///{os.path.join(ROOT_DIR, "temp", DB_NAME)}.db'


class TestingConfig(Config):
    ENV = True
    LOGGING_LEVEL = int(environ.get('LOGGING_LEVEL', default=5))
    LOGGING_FORMATTER = environ.get('LOGGING_FORMATTER', default='%(levelname)s::%(module)s: %(message)s')
    SECRET_KEY = environ.get('SECRET_KEY', default='8"79cpvp?xyCBPZV]T8~-m3"*0x>dm88Nm$PV]sW}AMq/Fj4zBa%fGt~Xa>emVw')
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', default=False) in [True, 'True']

    BCRYPT_LOG_ROUNDS = 4
    TESTING = True
    WTF_CSRF_ENABLED = False
    # DATABASE
    DB_NAME = "test"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(ROOT_DIR,"temp","test")}.db'
