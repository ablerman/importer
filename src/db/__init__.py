from sqlalchemy import create_engine
POSTGRES_URL = 'postgres://import_user:import_password@127.0.0.1/import_db'

engine = create_engine(POSTGRES_URL)


def get_connection():
    return engine.connect()
