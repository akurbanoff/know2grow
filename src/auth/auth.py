from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend
from src.config import SECRET

transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=transport,
    get_strategy=get_jwt_strategy,
)