from typing import List
from sqlalchemy.orm import relationship
from src.database import Base
from sqlalchemy import Column, String, Integer
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
#from src.oauth import OAuthAccount


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    hashed_password = Column(String)

#oauth_accounts: List[OAuthAccount] = relationship("OAuthAccount", lazy="joined")
