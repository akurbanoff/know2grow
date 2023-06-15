import os

import uvicorn
from drive import Client
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi_admin import enums
#from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Link, Dropdown, Model, Field
from fastapi_admin.widgets import filters, displays
from fastapi_users import InvalidPasswordException
from starlette import status
from starlette.staticfiles import StaticFiles

from src.auth.manager import google_oauth_client
from src.auth.routers import router as auth_router
from src.config import SECRET, SENTRY_CDN
from src.static.assets.text import cats_status_code_url

from src.static.routers import router as template_router
from src.crypto_news.routers import router as crypto_news_router
from src.education.routers import router as education_router
from src.binance.router import router as binance_router

from src.auth.auth import auth_backend
from src.auth.schemas import UserRead, UserCreate
from src.file_work import FileWork
from src.database import session, engine
from sqlalchemy import select, update, insert
from src.auth.models import User, PostClass, Admin, OAuthAccount
from passlib.hash import bcrypt
import bcrypt
import requests
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import sentry_sdk
from redis import asyncio as aio_redis

sentry_sdk.init(
    dsn=SENTRY_CDN,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)

# logging.basicConfig(level=logging.INFO, filename="app.log",filemode="w",
#                     format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title='know2grow',
    version='0.0.1'
)

# app.mount('/admin', admin_app)

app.mount('/static', StaticFiles(directory='static'), name='static')

#
# login_provider = UsernamePasswordProvider(
#     admin_model=Admin,
#     login_logo_url="https://preview.tabler.io/static/logo.svg"
# )



@app.on_event('startup')
async def take_redis():
    redis = aio_redis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')

    # await admin_app.configure(
    #     logo_url="https://preview.tabler.io/static/logo-white.svg",
    #     template_folders=["templates"],
    #     providers=[
    #         UsernamePasswordProvider(
    #             login_logo_url="https://preview.tabler.io/static/logo.svg", admin_model=Admin
    #         )
    #     ],
    #     redis=redis,
    # )


# @admin_app.register
# class Home(Link):
#     label = "Home"
#     icon = "fas fa-home"
#     url = "/"
#
#
# @admin_app.register
# class Content(Dropdown):
#     class UserResource(Model):
#         label = "User"
#         model = User
#         fields = ["id", "name", "email", "hashed_password", 'oauth_accounts']
#
#     class OAuthAccountResource(Model):
#         label = "OAuthAccount"
#         model = OAuthAccount
#         # filters = [
#         #     filters.Enum(enum=enums.ProductType, name="type", label="ProductType"),
#         #     filters.Datetime(name="created_at", label="CreatedAt"),
#         # ]
#         fields = ["id", "user_id", "user"]
#
#     class PostResource(Model):
#         label = 'Post'
#         model = PostClass
#         fields = ['id', 'title', 'links', 'summary']
#
#
#     label = "Content"
#     icon = "fas fa-bars"
#     resources = [UserResource, OAuthAccountResource, PostResource]



app.include_router(
    auth_router.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['Auth']
)

app.include_router(
    auth_router.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['Auth']
)

app.include_router(
    auth_router.get_oauth_router(google_oauth_client, auth_backend, SECRET),
    prefix="/auth/google",
    tags=["Auth"],
)

app.include_router(
    template_router
)

app.include_router(
    crypto_news_router
)

app.include_router(
    education_router
)

app.include_router(
    binance_router
)



# app.include_router(
#     auth_router.get_reset_password_router(),
#     prefix='/auth',
#     tags=['Auth']
# )

#
# app.include_router(
#     auth_router.get_oauth_router(google_oauth_client, auth_backend, SECRET, associate_by_email=True),
#     prefix="/auth/google",
#     tags=["Auth"],
# )
#
# app.include_router(
#     auth_router.get_oauth_associate_router(google_oauth_client, UserRead, SECRET),
#     prefix="/auth/associate/google",
#     tags=["Auth"],
# )


@app.post('/auth/change_password', tags=['Auth'])
async def change_password(email: str, new_password: str):
    '''
    Смена пароля с хэшированием.

    Параметры:
    - email(str): ввод почты, по которой будет браться юзер и меняться пароль
    - new_password(str): длина больше 8 без @ или эл почты в пароле, также должен быть хоть 1 символ в верхнем регистре.

    Return:
    - 200 OK
    '''

    rounds = 12
    salt = b'$2b$12$.......................'

    if len(new_password) < 8:
        raise InvalidPasswordException(
            reason="Пароль должен быть длиннее 8 символов."
        )
    if new_password.count('@') >= 1:
        raise InvalidPasswordException(
            reason="Пароль не должен быть равен электронной почте."
        )
    if new_password.islower():
        raise InvalidPasswordException(
            reason='Пароль должен содержать символы как в нижнем, так и в верхнем регистре.'
        )

    new_password = new_password.encode('utf-8')
    password = bcrypt.hashpw(password=new_password, salt=salt)

    async with session() as conn:
        stmt = update(User).values(hashed_password=password.decode('utf-8')).where(User.email == email)
        await conn.execute(stmt)
        await conn.commit()

    cats_response = requests.get(url=f'{cats_status_code_url}200')
    return 200



if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", log_level="info")