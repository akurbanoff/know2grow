from fastapi import FastAPI
from src.auth.routers import router as auth_router
from src.auth.auth import auth_backend
from src.auth.schemas import UserRead, UserUpdate, UserCreate
#from src.oauth import google_oauth_client

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
    auth_router.get_verify_router(UserRead),
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