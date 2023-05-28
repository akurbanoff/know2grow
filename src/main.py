import time

import uvicorn
from fastapi import FastAPI, Depends, UploadFile, File
from fastapi_users import InvalidPasswordException
from src.auth.routers import router as auth_router
from src.auth.auth import auth_backend
from src.auth.schemas import UserRead, UserUpdate, UserCreate
from src.config import *
#from src.auth.models import google_oauth_client, oauth_scheme
from src.auth.manager import UserManager
from src.utils import get_user_db
from fastapi.responses import JSONResponse
from src.database import session
from sqlalchemy import select, update
from src.auth.models import User
from passlib.hash import bcrypt
import bcrypt
import requests
import datetime
from src.google_drive.google_api import GoogleDrive
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache


app = FastAPI(
    title='know2grow',
    version='0.0.1'
)


@app.on_event('startup')
async def take_redis():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')


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

current_user = auth_router.current_user()

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

@app.post('/auth/change_password')
async def change_password(email: str, new_password: str, test_db: bool = False):
    rounds = 12
    salt = b'$2b$12$'#.......................'

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

    if not test_db:
        async with session() as conn:
            stmt = update(User).values(hashed_password=password.decode('utf-8')).where(User.email == email)
            await conn.execute(stmt)
            await conn.commit()

    return JSONResponse(content={
        'result': 'OK'
    })


@app.get('/get_crypto_news')
async def get_crypto_news(get_all: bool = False, currency: str = None, get_by_tag: str = None,
                          get_from_to: datetime.datetime = None, user=Depends(current_user)):
    url = f'https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTO_PANIC_API}'
    response = None

    if get_all:
        response = requests.get(url=url)
    else:
        try:
            if user.email:
                if currency is not None:
                    url = f'{url}&currencies={currency}'
                    response = requests.get(url=url)
                elif get_by_tag is not None:
                    url = f'{url}&search={get_by_tag}'
                    response = requests.get(url=url)
        except Exception as ex:
            return 'Скорее всего вы не вошли в аккаунт или вы ввели что то не так, попробуйте еще раз.'
    # elif get_from_to is not None:
    #     url = f'{url}&public=true&min_date=2022-05-01T00:00:00Z&max_date=2022-05-31T23:59:59Z'

    data = response.json()
    return data


@app.post('/oauth2')
async def oauth2_authenticate():
    drive = GoogleDrive().create_drive()
    return drive


@app.post('/add_photo')
async def add_photo(file: UploadFile = File(...)):#, drive: GoogleDrive = Depends(oauth2_authenticate)):
    filename = file.filename
    mime_type = GoogleDrive.mime_types.get(os.path.splitext(filename)[1], 'application/octet-stream') #file.content_type
    file_content = await file.read()
    folder_id = '1Swr1jDm1x8aHnMglfzzAaW-dG96qGCen'
    #print(filename, mime_type, file_content)
    try:
        GoogleDrive.upload_files(filename=filename, mime_type=mime_type, file_content=file_content, folder_id=folder_id)
    except Exception as ex:
        return ex

    return 200


@app.post('/add_new_edu_info')
async def add_new_edu_info(title: str, links: str, summary: str, photo):
    pass


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", log_level="info")