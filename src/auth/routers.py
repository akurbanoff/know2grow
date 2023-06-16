from fastapi_users import FastAPIUsers
from src.auth.models import User
from src.auth.manager import get_user_manager
from src.auth.auth import auth_backend


router = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)