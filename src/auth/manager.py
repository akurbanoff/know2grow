from typing import Optional, Union
from fastapi.responses import JSONResponse
from fastapi import Depends
from fastapi_users import IntegerIDMixin, BaseUserManager, InvalidPasswordException, schemas, models
from starlette import exceptions
from starlette.requests import Request
from starlette.responses import Response
from src.auth.models import User
from src.auth.schemas import UserCreate
from src.config import SECRET
from src.utils import get_user_db
import hashlib
from src.background_tasks import send_hello_to_new_user


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        send_hello_to_new_user.delay(user.name)
        print(f"User {user.id} has registered.")

    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, User],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Пароль должен быть длиннее 8 символов."
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Пароль не должен быть равен электронной почте."
            )
        if password.islower():
            raise InvalidPasswordException(
                reason='Пароль должен содержать символы как в нижнем, так и в верхнем регистре.'
            )

    async def forgot_password(
        self, user: models.UP, request: Optional[Request] = None
    ):
        new_password = ''
        if user.email == User.email:
            new_password = 'Qwerty6'
            User.hashed_password = new_password

        return new_password


    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user



async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)