from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

def make_engine():
    dsn = os.getenv("DB_DSN","postgresql://postgres:postgres@localhost:5432/danceapp")
    # Async driver
    if dsn.startswith("postgresql://"):
        dsn = dsn.replace("postgresql://","postgresql+asyncpg://",1)
    return create_async_engine(dsn, future=True, echo=False, pool_pre_ping=True)

engine = make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False, autocommit=False, class_=AsyncSession)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
