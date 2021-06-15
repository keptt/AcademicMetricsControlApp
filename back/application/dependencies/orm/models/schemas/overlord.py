from sqlalchemy     import Column, Integer, String, DateTime, Sequence, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime       import datetime

from ...db_config    import Base
# from .overlord      import Teacher, Student


class Human(Base):
    """
    Model of a human
    """
    __table_args__ = {'schema' : 'overlord'}
    __tablename__ = 'human'

    id              = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name            = Column(String(50), nullable=False)
    surname         = Column(String(50), nullable=False)
    name_prefix     = Column(String(100))
    surname_prefix  = Column(String(100))
    name_suffix     = Column(String(100))
    surname_suffix  = Column(String(100))
    patronimic      = Column(String(50))

    user            = relationship('User', uselist=False, back_populates='human')
    teacher         = relationship('Teacher', uselist=False, back_populates='human')
    student         = relationship('Student', uselist=False, back_populates='human')


class User(Base):
    """
    Model of a user
    """
    __table_args__ = {'schema' : 'overlord'}
    __tablename__ = 'app_user'

    id              = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    email           = Column(String(100), nullable=False, unique=True)
    password        = Column(String(100), nullable=False)
    role_id         = Column(Integer, ForeignKey('overlord.app_role.id', ondelete='SET NULL'))
    creation_dt     = Column(DateTime, server_default=func.now())
    expiration_dt   = Column(DateTime)
    human_id        = Column(Integer, ForeignKey('overlord.human.id', ondelete='SET NULL'))

    human           = relationship('Human', back_populates='user')
    role            = relationship('Role', back_populates='users')


class Role(Base):
    """
    Model of a role
    """
    __table_args__ = {'schema' : 'overlord'}
    __tablename__ = 'app_role'

    id          = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name        = Column(String(32), nullable=False)

    users       = relationship('User', back_populates='role')



