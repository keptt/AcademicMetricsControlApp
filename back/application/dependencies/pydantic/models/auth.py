from datetime import datetime

from typing     import List, Optional
from pydantic   import BaseModel


class Token(BaseModel):
    access_token:       str
    refresh_token:      str
    token_type:         str


class TokenData(BaseModel):
    username: Optional[str] = None


class Role(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Human(BaseModel):
    name:           Optional[str]
    surname:        Optional[str]
    name_prefix:    Optional[str]
    name_suffix:    Optional[str]
    surname_prefix: Optional[str]
    surname_suffix: Optional[str]
    patronimic:     Optional[str]

    class Config:
        orm_mode = True


class User(BaseModel):
    email:          str
    creation_dt:    Optional[datetime] = None
    expiration_dt:  Optional[datetime] = None
    role:           Role
    password:       Optional[str] = None
    personal_data:  Optional[Human]

    # class Config:
    #     orm_mode = True


class UserInfo(BaseModel):
    username: str # username is equal to email
    password: str


class RefreshTokenData(BaseModel):
    refresh_token: str


class Status(BaseModel):
    status: str


class CreatedUsers(BaseModel):
    quantity: int
