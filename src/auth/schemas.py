from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr, BaseModel


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class UserCreate(schemas.BaseUserCreate):
    name: str
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    name: str
    password: Optional[str]
    email: Optional[EmailStr]