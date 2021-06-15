from dotenv import load_dotenv

load_dotenv('./.env')

from application.dependencies.orm.db_config import sessions, engine_main, Base
from application.dependencies.orm.models.schemas.overlord import *
from application.dependencies.orm.models.schemas.parquet import *

from application.dependencies.admin.auth import get_hashed_password

from sqlalchemy import schema


session_main = sessions['main']()


if not engine_main.dialect.has_schema(engine_main, 'overlord'):
    engine_main.execute(schema.CreateSchema('overlord'))

if not engine_main.dialect.has_schema(engine_main, 'parquet'):
    engine_main.execute(schema.CreateSchema('parquet'))


Base.metadata.create_all(bind=engine_main) # , tables=table_objects)


session_main.add(DayOfWeek(name='Monday'    , short_name='MON'))
session_main.add(DayOfWeek(name='Tuesday'   , short_name='TUE'))
session_main.add(DayOfWeek(name='Wednesday' , short_name='WED'))
session_main.add(DayOfWeek(name='Thursday'  , short_name='THU'))
session_main.add(DayOfWeek(name='Friday'    , short_name='FRI'))
session_main.add(DayOfWeek(name='Saturday'  , short_name='SAT'))
session_main.add(DayOfWeek(name='Sunday'    , short_name='SUN'))



session_main.add(Role(name='SUADMIN'))
session_main.add(Role(name='AMDIN'))
session_main.add(Role(name='STUDENT'))
session_main.add(Role(name='TEACHER'))
session_main.add(Role(name='CLASSREP'))


session_main.add(User(email='broodmaster', password=get_hashed_password('broodm@ster'), role_id=1))


session_main.commit()
