from fastapi import FastAPI, Depends
from fastapi_users import InvalidPasswordException
from src.auth.routers import router as auth_router
from src.auth.auth import auth_backend
from src.auth.schemas import UserRead, UserUpdate, UserCreate
#from src.oauth import google_oauth_client
from src.auth.manager import UserManager
from fastapi.responses import JSONResponse
from src.database import session
from sqlalchemy import select, update
from src.auth.models import User
from passlib.hash import bcrypt
import bcrypt


app = FastAPI(
    title='know2grow',
    version='0.1'
)

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
    auth_router.get_reset_password_router(),
    prefix='/auth',
    tags=['Auth']
)

# app.include_router(
#     auth_router.get_oauth_router(google_oauth_client, auth_backend, "SECRET"),
#     prefix="/auth/google",
#     tags=["auth"],
# )

@app.post('/auth/change_password')
async def change_password(email: str, new_password: str, test_db: bool = False):
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

    if not test_db:
        async with session() as conn:
            stmt = update(User).values(hashed_password=password.decode('utf-8')).where(User.email == email)
            await conn.execute(stmt)
            await conn.commit()

    return JSONResponse(content={
        'result': 'OK'
    })