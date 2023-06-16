from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, BINARY, LargeBinary
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import Column, Integer, ForeignKey
from src.database import Base


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="cascade"), nullable=False)
    user = relationship("User", back_populates="oauth_accounts")


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    hashed_password = Column(String)

    oauth_accounts = relationship("OAuthAccount", back_populates="user")


class PostClass(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    links = Column(String)
    summary = Column(String)
    photo = Column(LargeBinary)


class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String, unique=True)