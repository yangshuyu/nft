import datetime
import os
from datetime import timedelta

from config.default import Config


class DevelopmentConfig(Config):
    DEBUG = True

    SIGNATURE = True

    # SERVER
    SERVER_SCHEME = "http"
    SERVER_DOMAIN = "10.156.10.119:5002"

    LAYER_FILE = os.environ.get(
        'LAYER_FILE',
        '{}/{}'.format(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'file/layers')
    )

    # SQL
    PSQL_USER = ""
    PSQL_PASSWORD = ""
    PSQL_PORT = "5432"
    PSQL_DATABASE = "nft"
    PSQL_HOST = "127.0.0.1"
    # PSQL_USER = "ecpostgres"
    # PSQL_PASSWORD = "ecpostgres123"
    # PSQL_PORT = "5436"
    # PSQL_DATABASE = "ec"
    # PSQL_HOST = "10.122.100.226"

    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
        PSQL_USER, PSQL_PASSWORD, PSQL_HOST, PSQL_PORT, PSQL_DATABASE
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
