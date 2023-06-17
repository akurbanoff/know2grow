import datetime
import requests
from fastapi import APIRouter, Depends
from src.auth.routers import router as auth_router
from src.config import CRYPTO_PANIC_API
from src.auth.current_user import current_user


router = APIRouter(
    tags=["News"]
)


@router.get('/get_crypto_news')
async def get_crypto_news(get_all: bool = False, currency: str = None, get_by_tag: str = None,
                          get_from: datetime.date = None, get_to: datetime.date = None, user=Depends(current_user)):
    '''
    Получает новости про криптовалюту и эту сферу в целом.

    Параметры:
    - get_all (bool): если значение True, то будут получены 100 последних новостей.
    - currency (str): поиск по типу валюты. Вводите в формате BTC, ETH и тд.
    - get_by_tag (str): ключевое слово для поиска.
    - get_from/to (datatime): даты публикации новостей с какого-то числа и по какое-то число в формате год-месяц-число.

    Примечание:
    - Для использования некоторых параметров требуется авторизация пользователя.
    - Функция возвращает список новостей.

    Формат новости:

    {

      "kind": "news",

      "domain": "ambcrypto.com",

      "source": {

        "title": "AMBCrypto",

        "region": "en",

        "domain": "ambcrypto.com",

        "path": null
      },

      "title": "How Boring Punks set the stage for NFT revival",

      "published_at": "2023-06-16T13:30:43Z",

      "slug": "How-Boring-Punks-set-the-stage-for-NFT-revival",

      "id": 18592830,

      "url": "https://cryptopanic.com/news/18592830/How-Boring-Punks-set-the-stage-for-NFT-revival",

      "created_at": "2023-06-16T13:30:43Z",

      "votes": {

        "negative": 0,

        "positive": 0,

        "important": 0,

        "liked": 0,

        "disliked": 0,

        "lol": 0,

        "toxic": 0,

        "saved": 0,

        "comments": 0

      }
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

                elif get_from is not None and get_to is not None:
                    get_from = str(get_from).replace(' ', '-').replace('.', '-')
                    get_to = str(get_to).replace(' ', '-').replace('.', '-')
                    #if datetime.datetime.strptime(get_from, '%y-%m-%d') and datetime.datetime.strptime(get_to, '%y-%m-%d'):
                    url = f'{url}&public=true&min_date={get_from}T00:00:00Z&max_date={get_to}T23:59:59Z'
                    response = requests.get(url=url)

        except Exception as ex:
            return 'Скорее всего вы не вошли в аккаунт или вы ввели что то не так, попробуйте еще раз.'
    # elif get_from_to is not None:
    #     url = f'{url}&public=true&min_date=2022-05-01T00:00:00Z&max_date=2022-05-31T23:59:59Z'

    data = response.json()
    return data