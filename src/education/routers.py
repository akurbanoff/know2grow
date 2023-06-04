import requests
from fastapi import APIRouter
from sqlalchemy import insert, select

from src.auth.models import PostClass
from src.database import engine
from src.static.assets.text import cats_status_code_url

router = APIRouter(
    tags=["Education"]
)

@router.post('/add_new_edu_post')
async def add_new_edu_info(title: str, links: str, summary: str):
    '''
    Добавление новой статьи в бд.
    - title: заголовок
    - links: ссылки, которые использовались при написании статьи
    - summary: основной текст
    Возвращает код 201 если все успешно загрузилось.
    '''
    async with engine.begin() as db:
        stmt = insert(PostClass).values(title=title, links=links, summary=summary)
        await db.execute(stmt)
        await db.commit()

    cats_response = requests.get(url=f'{cats_status_code_url}200')
    return 201


@router.get('/get_edu_posts')
async def get_edu_posts():
    '''
    Возвращает все посты, которые есть в базе в json формате, с полями:
    - id
    - title
    - links
    - summary
    '''
    async with engine.begin() as db:
        stmt = select(PostClass).order_by(PostClass.id)
        posts = await db.execute(stmt)
        posts = posts.fetchall()

    json_data = dict()
    for post in posts:
        json_data = {
            'id': post[0],
            'title': post[1],
            'links': post[2],
            'summary': post[3]
        }

    return json_data