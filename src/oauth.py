# from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTable
# from sqlalchemy import Column, Integer, ForeignKey
# from sqlalchemy.orm import declared_attr
#
# from src.auth.models import User
# from src.config import CLIENT_ID, CLIENT_SECRET
# from src.database import Base
# from httpx_oauth.clients.google import GoogleOAuth2
#
#
# google_oauth_client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
#
# class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
#     id = Column(Integer, primary_key=True)
#
#     @declared_attr
#     def user_id(cls):
#         return Column(Integer, ForeignKey(User.id, ondelete="cascade"), nullable=False)
# import secrets
#
# secret_key = secrets.token_hex(32)
#
# print(secret_key)
