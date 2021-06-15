import os
import aioredis

import sqlalchemy_filters
from application.patches.sqlalchemy_filters import get_query_models

sqlalchemy_filters.models.get_query_models = get_query_models #* patch sqlalchemy filters broken function


from fastapi                    import FastAPI, Request, status, Depends
from fastapi.middleware.cors    import CORSMiddleware
from fastapi.responses          import JSONResponse
from sqlalchemy.exc             import DatabaseError

from dotenv import load_dotenv

load_dotenv('./.env')

from application.dependencies.redis.config import redis_plugin, depends_redis, redis_config
from application.routers import auth, reports, initdata

from colorama import init, Fore
init()


if not os.getenv('SECRET_KEY') or not os.getenv('ALGORITHM') or not os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'):
    raise Exception('SECRET_KEY or ALGORITHM or ACCESS_TOKEN_EXPIRE_MINUTES is empty')


os.environ['ROLE_SUADMIN']  = 'SUADMIN'
os.environ['ROLE_ADMIN']    = 'AMDIN'
os.environ['ROLE_STUDENT']  = 'STUDENT'
os.environ['ROLE_TEACHER']  = 'TEACHER'
os.environ['ROLE_CLASSREP'] = 'CLASSREP'

COMMON_PREFIX               = '/api'


subapp = FastAPI()

subapp.include_router(auth.router)
subapp.include_router(initdata.router)
subapp.include_router(reports.router)


@subapp.exception_handler(DatabaseError)
async def db_error_exception_handler(request: Request, exc: DatabaseError):
    print(Fore.RED + 'Error:', str(exc) + Fore.RESET)
    return JSONResponse(content={'detail': f'Database unavailable'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@subapp.exception_handler(Exception)
async def common_exception_handler(request: Request, exc: Exception):
    print(Fore.RED + 'Error:', str(exc) + Fore.RESET)
    return JSONResponse(content={'detail': f'Intervnal server error'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@subapp.get('/')
async def root_get(cache: aioredis.Redis=Depends(depends_redis)):
    return dict(ping=await cache.ping())


app = FastAPI()

@app.on_event('startup')
async def on_startup():
    print(redis_config)
    print(redis_config.redis_host)
    await redis_plugin.init_app(subapp, config=redis_config)  # initializes subapps state which we than transfer to app's state
    await redis_plugin.init()


@app.on_event('shutdown')
async def on_shutdown():
    await redis_plugin.terminate()


subapp_state = subapp.state
app.mount(COMMON_PREFIX, subapp) # mount to create a common prefix

app.state = subapp_state

origins = (os.getenv('ALLOWED_ORIGINS') and os.getenv('ALLOWED_ORIGINS').split(';')) or ['*']

print('ALLOWED ORIGINS:', origins)


app.add_middleware(
    CORSMiddleware
    , allow_origins=origins
    , allow_credentials=True
    , allow_methods=['*']
    , allow_headers=['*']
    , expose_headers=['*']
)
