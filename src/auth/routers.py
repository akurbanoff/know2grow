from fastapi_users import FastAPIUsers
from .models import User
from .manager import get_user_manager
from .auth import auth_backend

router = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)