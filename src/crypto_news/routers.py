import datetime

import requests
from fastapi import APIRouter, Depends
from src.auth.routers import router as auth_router
from src.config import CRYPTO_PANIC_API

router = APIRouter(
    tags=["News"]
)

current_user = auth_router.current_user()

@router.get('/get_crypto_news')
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