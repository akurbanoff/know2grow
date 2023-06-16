from fastapi import APIRouter, Depends
import bcrypt
import requests
import validate_email
from fastapi_users import InvalidPasswordException
from sqlalchemy import update

from src.auth.current_user import current_user
from src.auth.models import User
from src.database import session, engine
from src.file_work import FileWork
from src.google_api import drive
from src.static.assets.text import cats_status_code_url

account_router = APIRouter(
    tags=['Auth']
)

@account_router.get('/profile')
async def get_profile(user = Depends(current_user)):
    try:
        photo = drive.get_file_by_name(name=user.name)
    except Exception as ex:
        photo = FileWork().get_file(filename='default_photo.png')
    data = {
        'username': user.name,
        'email': user.email,
        'photo': photo
    }
    return data


@account_router.post('/auth/change_password')
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


@account_router.post('/auth/change_name')
async def change_name(new_name: str, user=Depends(current_user)):
    async with engine.begin() as db:
        stmt = update(User).values(name=new_name).where(User.email == user.email)
        await db.execute(stmt)
        await db.commit()
    return f'Вы изменили {user.name} на {new_name}.'


@account_router.post('/auth/change_email')
async def change_email(new_email, user = Depends(current_user)):
    if not validate_email.validate_email(email=new_email):
        return 'Указанный адрес почты недействителен либо вы совершили ошибку. Пожалуйста введите адрес почты в формате example@something.ru'

    async with engine.begin() as db:
        stmt = update(User).values(email=new_email).where(User.name == user.name)
        await db.execute(stmt)
        await db.commit()
    return f'Вы сменили {user.email} на {new_email}'