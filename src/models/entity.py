from sqlalchemy import Column, ForeignKey, Integer, String

from .base import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)


class Token(Base):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    token = Column(String, unique=True, nullable=False)


class Storage(Base):
    __tablename__ = 'storage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('users.id'))
    file_name = Column(String)
    file_path = Column(String)
