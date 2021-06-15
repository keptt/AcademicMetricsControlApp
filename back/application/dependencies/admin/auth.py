import os
import datetime
import aioredis
import bcrypt

from ..redis.config import redis_plugin
from fastapi_plugins import depends_redis

from uuid import uuid4
from sqlalchemy.orm     import Session
from fastapi            import Depends, HTTPException, status
from fastapi.security   import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose               import JWTError, jwt
from passlib.context    import CryptContext

from ..orm.routines.auth            import db_get_user
from ..pydantic.models.auth         import TokenData
from ..orm.utils                    import DBGetter
from ..orm.models.schemas.overlord  import User

from ..common.utils import to_unix_time


pwd_context     = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme   = OAuth2PasswordBearer(tokenUrl='token')


def generate_access_token_by_userdata(user): # sqlalchemy user object
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    is_nonexpired = check_user_expired(user)
    if not is_nonexpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires    = datetime.timedelta(minutes=abs(int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES') or 1440)))
    refresh_token_expires   = datetime.timedelta(minutes=abs(int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES') or 43200)))


    atjti = str(uuid4().hex)
    rtjti = str(uuid4().hex)

    access_token_exp_time   = to_unix_time(get_token_exp_time(access_token_expires))
    refresh_token_exp_time  = to_unix_time(get_token_exp_time(refresh_token_expires))

    access_token = create_token(
        data={'sub': user.username, 'jti': atjti, 'rtjti': rtjti, 'rtexp': refresh_token_exp_time}, expires_delta=access_token_expires
    )
    refresh_token = create_token(
        data={'sub': user.username, 'is_refresh': True, 'jti': rtjti, 'atjti': atjti, 'atexp': access_token_exp_time}, expires_delta=refresh_token_expires
    )
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


def get_token_exp_time(expires_delta: datetime.timedelta): #? Optional[datetime.timedelta]=None
    return datetime.datetime.utcnow() + expires_delta


def create_token(data: dict, expires_delta: datetime.timedelta=datetime.timedelta(minutes=15)): #? Optional[datetime.timedelta]=None
    to_encode = data.copy()
    expire = get_token_exp_time(expires_delta)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))

    return encoded_jwt


async def red() -> aioredis.Redis: # delete it
    yield await redis_plugin()


async def validate_token(cache: aioredis.Redis=Depends(depends_redis), db: Session=Depends(DBGetter('main')), token: str=Depends(oauth2_scheme), is_refresh=False):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    malformed_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Token is malformed',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
    except JWTError as exc:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(exc),
                    headers={'WWW-Authenticate': 'Bearer'},
                )

    if not payload.get('jti'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is malformed',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if cache:
        blacklisted_token = await cache.get(payload['jti'])
        if blacklisted_token:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token has been blacklisted and can\'t be used again',
                    headers={'WWW-Authenticate': 'Bearer'},
                )

    if is_refresh:
        if payload.get('is_refresh') == True:
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token is not a refresh token',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        if payload.get('atjti'):
            pass
        else:
            raise malformed_exception
    else:
        if payload.get('is_refresh') == True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Refresh token can\'t be used as an access token',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        if payload.get('rtjti'):
            pass
        else:
            raise malformed_exception

    username: str = payload.get('sub')

    if username is None:
        raise credentials_exception

    token_data = TokenData(username=username) # what am I even doing here? useless. This was in the example in the docs or smth tho


    user = db_get_user(db, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


def seconds_from_now(timestamp):
    t = int( (datetime.datetime.utcfromtimestamp(int(timestamp)) - datetime.datetime.utcnow()).total_seconds() )
    if t > 0:
        return t
    return 1 # means that token already expired so we set it blacklist time to 1 second (might as well have not added it to blacklist at all)


async def blacklist_token(db, token, cache: aioredis.Redis, is_refresh=False):
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])

        if not cache:
            print('Unable to blacklist token, NO CACHE')
            return

        await cache.set(payload['jti'], 1, expire=seconds_from_now(payload['exp'])) #! set expire here

        if is_refresh:
            access_token_jti = payload['atjti'] #! also atexp - access token exp
            await cache.set(access_token_jti, 1, expire=seconds_from_now(payload['atexp'])) #! set expire here
        else:
            refresh_token_jti = payload['rtjti'] #! also atexp - access token exp
            await cache.set(refresh_token_jti, 1, expire=seconds_from_now(payload['rtexp'])) #! set expire here
    except Exception as exc:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Something went wrong during auth',
                    headers={'WWW-Authenticate': 'Bearer'},
                )


def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)


def authenticate_user(db, username: str, password: str):
    user = db_get_user(db, username)
    if not user:
        return False
    try:
        if not check_password(password, user.password):
            raise Exception()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User authentication refused due to the wrong password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user


def check_user_expired(user):
    return (user.expiration_dt and user.expiration_dt > datetime.datetime.now()) or not user.expiration_dt


def check_if_admin(current_user: User=Depends(validate_token)):
    if not current_user.isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access forbidden',
            headers={'WWW-Authenticate': 'Bearer'},
        )


def check_if_user(current_user: User=Depends(validate_token)): # we don't need to do anything else to validate if client is a "user"
    pass
