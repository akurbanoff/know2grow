from typing import List
from sqlalchemy.orm import relationship
from src.database import Base
from sqlalchemy import Column, String, Integer
#from src.oauth import OAuthAccount


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

#oauth_accounts: List[OAuthAccount] = relationship("OAuthAccount", lazy="joined")
