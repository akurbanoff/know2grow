import os

import uvicorn
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi_admin import enums
#from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Link, Dropdown, Model, Field
from fastapi_admin.widgets import filters, displays
from fastapi_users import InvalidPasswordException
from starlette import status
from starlette.staticfiles import StaticFiles

from src.auth.routers import router as auth_router
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
from redis import asyncio as aio_redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
#from fastapi_admin.app import app as admin_app
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Annotated
from src.google_drive.google_api import Drive


SECRET_KEY = "7adaa99a3dc424cfeed0dc75cdf0fde4514e9c9d52a6ca89418a89c2f8b7460c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


# @app.post('/upload_file', tags=['Posts'])
# async def upload_file(file: UploadFile = File(...)):
#     drive = Drive()
#     drive.upload_file(file=file, name=file.filename, mime_type=file.content_type)
#     # file_work = FileWork()
#     # file_work.create_file(file=file, filename=file.filename)
#
#     cats_response = requests.get(url=f'{cats_status_code_url}201')
#     return 201
#
#
# @app.get('/get_file', tags=['Posts'])
# async def get_file(filename: str):
#     drive = Drive()
#     return drive.get_file_by_name(name=filename)
#
#
# @app.get('/get_all_files', tags=['Posts'])
# async def get_all_files():
#     drive = Drive()
#     return drive.get_all_files()



# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class TokenData(BaseModel):
#     username: str | None = None
#
#
# class UserInDB(User):
#     hashed_password: str
#
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
#
# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)
#
#
# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
#
#
# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
#
# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
#     db_users = None
#     async with engine.begin() as db:
#         stmt = select(User)
#         db_users = await db.execute(stmt)
#
#
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(db_users, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
#
#
# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
#
#
# @app.post("/token", response_model=Token)
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ):
#     db_users = None
#     async with engine.begin() as db:
#         stmt = select(User)
#         db_users = await db.execute(stmt)
#
#     user = authenticate_user(db_users, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", log_level="info")