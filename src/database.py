from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base


db_url = ''

Base = declarative_base()

engine = create_async_engine(url=db_url)
session = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with session() as s:
        return s
