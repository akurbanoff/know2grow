from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr, BaseModel

schemas.BaseUserCreate
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "oauth_accounts",
            },
        )

class UserUpdate(BaseModel):
    name: str
    password: Optional[str]
    email: Optional[EmailStr]