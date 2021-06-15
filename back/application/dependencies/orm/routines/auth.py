from sqlalchemy.orm import Session
from typing import List


from ..models.schemas.overlord import User, Human, Role
from ...pydantic.models import User as PydanticUser
from ...admin.auth import get_hashed_password
from ...common import exceptions

def db_get_user(db: Session, username: str):
    user = db.query(User).filter(User.email == username).first()

    if user:
        return user
    return None


def create_user(db: Session, userdata: PydanticUser):
    role = Role(
        name=userdata.role.name
    )

    human = None

    if userdata.personal_data:
        human = Human(
            name=userdata.personal_data.name
            , surname=userdata.personal_data.patronimic
            , name_prefix=userdata.personal_data.patronimic
            , name_suffix=userdata.personal_data.patronimic
            , surname_prefix=userdata.personal_data.patronimic
            , surname_suffix=userdata.personal_data.patronimic
            , patronimic=userdata.personal_data.patronimic
        )

    try:
        user = User(
            email=userdata.email
            , expiration_dt=userdata.expiration_dt # if exporation_dt is not set then it will be None
            , role=role
            , human=human
            , password=get_hashed_password(userdata.password)
        )
        db.add(user)
        db.commit()
    except:
        raise exceptions.UserCreationError(f'Error while creating user "{userdata.email}"')

    return user


def create_users(db: Session, usersdata: List[PydanticUser]):
    for user in usersdata:
        create_user(db, user)
    return len(usersdata)


def remove_user(db: Session, username: str, user: User):
    if not user.role.name == os.getenv('ROLE_ADMIN') or user.role.name == os.getenv('ROLE_SUADMIN'):
        raise ...

    query = db.query(User).filter(User.email == username)
    user_to_remove = query.first()
    if not user_to_remove:
        return {}

    if user_to_remove.role.name == os.getenv('ROLE_ADMIN') and user.role.name != os.getenv('ROLE_SUADMIN'):
        raise ...

    if user_to_remove.role.name == os.getenv('ROLE_SUADMIN'):
        raise ...

    query.delete()
    db.commit()

    return user_to_remove


# def update_user(db: Session, username: str, user: User):
#     if not user.role.name == os.getenv('ROLE_ADMIN') or user.role.name == os.getenv('ROLE_SUADMIN'):
#         raise ...

#     query = db.query(User).filter(User.email == username)
#     user_to_remove = query.first()
#     if not user_to_remove:
#         return {}
#     ##! update update

#     if user_to_remove.role.name == os.getenv('ROLE_ADMIN') and user.role.name != os.getenv('ROLE_SUADMIN'):
#         raise ...

#     if user_to_remove.role.name == os.getenv('ROLE_SUADMIN'):
#         raise ...

#     query.delete()
#     db.commit()

#     return user_to_remove


# def update_user_(db, username: str, user: User):
    



# def update_self(db: Session, username: str, user: User):
#     if not user.role.name == os.getenv('ROLE_ADMIN') or user.role.name == os.getenv('ROLE_SUADMIN'):
#         raise ...

#     query = db.query(User).filter(User.email == username)
#     user_to_remove = query.first()
#     if not user_to_remove:
#         return {}
#     ##! update update

#     if user_to_remove.role.name == os.getenv('ROLE_ADMIN') and user.role.name != os.getenv('ROLE_SUADMIN'):
#         raise ...

#     if user_to_remove.role.name == os.getenv('ROLE_SUADMIN'):
#         raise ...

#     query.delete()
#     db.commit()

#     return user_to_remove
