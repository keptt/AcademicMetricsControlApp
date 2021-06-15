from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from os import getenv

from dotenv import load_dotenv

load_dotenv('./.env')


login_main       = getenv('LOGIN_MAIN')
password_main    = getenv('PASSWORD_MAIN')
hostname_main    = getenv('HOSTNAME_MAIN')
dbname_main      = getenv('DBNAME_MAIN')
port_main        = getenv('PORT_MAIN')


engine_main   = create_engine(f'postgresql+psycopg2://{login_main}:{password_main}@{hostname_main}:{port_main}/{dbname_main}', max_identifier_length=100, pool_size=20, max_overflow=0)


print('engine_main:', engine_main)

sessions = {'main':     sessionmaker(bind=engine_main)}

Base = declarative_base()
