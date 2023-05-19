from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseOAuthAccountTable, SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import declared_attr
from src.database import Base
from httpx_oauth.clients.google import GoogleOAuth2


# google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")
#
# class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
#     id = Column(Integer, primary_key=True)
#
#     @declared_attr
#     def user_id(cls):
#         return Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)