from sqlalchemy.orm import Session
from fastapi        import APIRouter, Depends, HTTPException, status

from typing import List

import aioredis
from  fastapi_plugins   import depends_redis

from ..dependencies.common import exceptions

from ..dependencies.orm.utils           import DBGetter
from ..dependencies.orm.models          import overlord
from ..dependencies.orm.routines        import auth  as auth_db_routine
from ..dependencies.pydantic.models     import auth  as auth_pydantic_model_controller
from ..dependencies.admin               import auth  as admin_auth_utils


router = APIRouter()


@router.post('/token', response_model=auth_pydantic_model_controller.Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):
async def login_for_access_token(userinfo: auth_pydantic_model_controller.UserInfo, db: Session=Depends(DBGetter('main'))):
    user = admin_auth_utils.authenticate_user(db, userinfo.username, userinfo.password)

    return admin_auth_utils.generate_access_token_by_userdata(user)


@router.post('/refresh', response_model=auth_pydantic_model_controller.Token)
async def refresh_access_token(refreshTokenData: auth_pydantic_model_controller.RefreshTokenData, db: Session=Depends(DBGetter('main')), cache: aioredis.Redis=Depends(depends_redis)):
    user = await admin_auth_utils.validate_token(cache, db, refreshTokenData.refresh_token, is_refresh=True)
    await admin_auth_utils.blacklist_token(db, refreshTokenData.refresh_token, is_refresh=True, cache=cache)

    return admin_auth_utils.generate_access_token_by_userdata(user)


@router.delete('/token', response_model=auth_pydantic_model_controller.Status)
async def destroy_access_token(access_token: str=Depends(admin_auth_utils.oauth2_scheme), db: Session=Depends(DBGetter('main')), cache: aioredis.Redis=Depends(depends_redis)):
    await admin_auth_utils.validate_token(cache, db, access_token)
    await admin_auth_utils.blacklist_token(db, access_token, cache=cache) # how to blacklist refresh token also? maybe I shouldn't even do it

    return {'status': 'success'}


@router.get('/users/me', response_model=auth_pydantic_model_controller.User)
def get_user_me(current_user: overlord.User=Depends(admin_auth_utils.validate_token)):
    return auth_pydantic_model_controller.User(
           email=current_user.email
           , creation_dt=current_user.creation_dt
           , expiration_dt=current_user.expiration_dt
           , role=current_user.role
           , personal_data=current_user.human
        )


# create user (only suadmin can create or delte admins and noone can touch suadmin)
@router.post('/user', response_model=auth_pydantic_model_controller.User)
def post_user(userdata: auth_pydantic_model_controller.User, db: Session=Depends(DBGetter('main')), current_user: overlord.User=Depends(admin_auth_utils.validate_token)):
    try:
        created_user = auth_db_routine.create_user(userdata)
    except exceptions.UserCreationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error during posting the user',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return created_user


# create users
@router.post('/users', response_model=auth_pydantic_model_controller.User)
def post_users(usersdata: List[auth_pydantic_model_controller.User], db: Session=Depends(DBGetter('main')), current_user: overlord.User=Depends(admin_auth_utils.validate_token)):
    try:
        created_users_num = auth_db_routine.create_users(db, usersdata)
    except exceptions.UserCreationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error during posting users',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return auth_pydantic_model_controller.CreatedUsers(quantity=created_users_num}


# @router.delete('/user/{username}', response_model=auth_pydantic_model_controller.User)
# def delete_user(username: str, db: Session=Depends(DBGetter('main')), current_user: overlord.User=Depends(admin_auth_utils.validate_token)):
#     try:
#         removed_user = auth_db_routine.remove_user(db, username, current_user)
#     except exceptions.UserCreationError as exc:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(exc),
#             headers={'WWW-Authenticate': 'Bearer'},
#         )
#     except Exception as exc:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail='Error during the user removal',
#             headers={'WWW-Authenticate': 'Bearer'},
#         )
#     return removed_user


# @router.put('/user/{username}', response_model=auth_pydantic_model_controller.User)
# def update_user(username: str, db: Session=Depends(DBGetter('main')), current_user: overlord.User=Depends(admin_auth_utils.validate_token)):
#     try:
#         updated_user = auth_db_routine.update_user(db, username, current_user)
#     except exceptions.UserCreationError as exc:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(exc),
#             headers={'WWW-Authenticate': 'Bearer'},
#         )
#     except Exception as exc:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail='Error during the user update',
#             headers={'WWW-Authenticate': 'Bearer'},
#         )
#     return updated_user
