from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from src.binance.router import socket_binance
from src.crypto_news.routers import get_crypto_news
from src.education.routers import get_edu_posts
from src.auth.routers import router as auth_router

from src.static.assets.text import buttons, edu_buttons

router = APIRouter(
    tags=["Pages"]
)

templates = Jinja2Templates(directory='./static/html')


@router.get('/main')
def get_main_temp(request: Request):
    return templates.TemplateResponse('main.html', {'request': request, 'title': 'Главная страница', 'buttons': buttons})


@router.get('/chart/{currency}')
def get_chart_temp(request: Request, currency = Depends(socket_binance)):
    return templates.TemplateResponse('chart.html', {'request': request, 'title': 'График', 'buttons': buttons,
                                                     'currency': currency})


@router.get('/news/?{get_all}&{currency}&{get_by_tag}')
def get_news_temp(request: Request, news = Depends(get_crypto_news)):
    return templates.TemplateResponse('news.html', {'request': request, 'title': 'Новости', 'buttons': buttons,
                                                    'news': news})


@router.get('/education')
def get_edu_temp(request: Request, edu_posts = Depends(get_edu_posts)):
    return templates.TemplateResponse('edu_news.html', {'request': request, 'title': 'Образование', 'buttons': buttons,
                                                        'edu_buttons': edu_buttons, 'edu_news': edu_posts})


@router.post('/auth/register')
def get_reg_temp(request: Request):
    return templates.TemplateResponse('')