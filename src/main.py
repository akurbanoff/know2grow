import os
import time
import uvicorn
import asyncio
from fastapi import FastAPI, Depends, UploadFile, File
from fastapi_users import InvalidPasswordException
from src.auth.routers import router as auth_router
from src.auth.auth import auth_backend
from src.auth.schemas import UserRead, UserUpdate, UserCreate
from src.config import CRYPTO_PANIC_API, BINANCE_API, BINANCE_SECRET_KEY
#from src.auth.models import google_oauth_client, oauth_scheme
from src.auth.manager import UserManager
from src.file_work import FileWork
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
from binance import AsyncClient
from binance.streams import BinanceSocketManager


app = FastAPI(
    title='know2grow',
    version='0.0.1'
)


@app.on_event('startup')
async def take_redis():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')


async def create_binance_client():
    binance_client = await AsyncClient.create(api_key=BINANCE_API, api_secret=BINANCE_SECRET_KEY)
    return binance_client


async def create_binance_manager(binance_client= Depends(create_binance_client)):
    binance_manager = BinanceSocketManager(binance_client, user_timeout=60)

    return binance_manager


async def process_message(msg):
    return msg


@app.get('/socket_binance')
async def socket_binance(currency: str, binance_manager: BinanceSocketManager = Depends(create_binance_manager)):
    '''
    Сокет соединение с бинансом. Длится 60 секунд, но походу бесконечно.
    - currency: принимает валюту по которой запрашиваются данные в формате тикера - BTCUSDT, ETHUSDT

    Возвращает данные в формате:
    {
      "e": "trade", - тип события, который указывает на тип транзакции.
      "E": 1685352493842, -  время события в миллисекундах.
      "s": "BTCUSDT", - символ пары торгов
      "t": 3128786077, - ID сделки.
      "p": "27892.87000000", - цена по которой произошла сделка.
      "q": "0.00181000", - количество базовой валюты, которое было продано или куплено.
      "b": 21277176651, - ID покупателя.
      "a": 21277175869, - ID продавца.
      "T": 1685352493842, - время выполнения операции в миллисекундах.
      "m": false, - флаг режима: true - если сделка происходит за пределами стакана (вне очереди), и false - если сделка происходит внутри стакана.
      "M": true - флаг maker: true - если покупатель является создателем спроса (maker), и false - если покупатель является исполнителем заявки (taker).
    }
    '''
    ts = binance_manager.trade_socket(symbol=currency)
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            return res



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

    return JSONResponse(content={
        'result': 'OK'
    })


@app.get('/get_crypto_news')
async def get_crypto_news(get_all: bool = False, currency: str = None, get_by_tag: str = None,
                          get_from_to: datetime.datetime = None, user=Depends(current_user)):
    '''
    Получает новости про криптовалюту и эту сферу в целом.

    Параметры:
    - get_all (bool): если значение True, то будут получены 100 последних новостей.
    - currency (str): поиск по типу валюты. Вводите в формате BTC, ETH и тд.
    - get_by_tag (str): ключевое слово для поиска.
    - get_from_to (datatime): даты публикации новостей с какого-то числа и по какое-то число.

    Примечание:
    - Для использования некоторых параметров требуется авторизация пользователя.
    - Функция возвращает список новостей.
    '''
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


# @app.post('/oauth2')
# async def oauth2_authenticate():
#     drive = GoogleDrive().create_drive()
#     return drive


@app.post('/add_photo')
async def add_photo(file: UploadFile = File(...)):#, drive: GoogleDrive = Depends(oauth2_authenticate)):
    file_work = FileWork()
    file_work.create_file(file=file)

    return 201

@app.get('/get_photo')
async def get_photo(file: UploadFile = File(...)):
    file_work = FileWork()
    return file_work.get_file(filename=file.filename)




@app.post('/add_new_edu_info')
async def add_new_edu_info(title: str, links: str, summary: str, photo):
    pass


@app.on_event('shutdown')
async def shutdown(binance_client=Depends(create_binance_client)):
    await binance_client.close_connection()


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", log_level="info")