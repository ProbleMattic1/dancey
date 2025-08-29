import os, asyncpg
from typing import Optional

_pool: Optional[asyncpg.Pool] = None
DSN = os.getenv("DB_DSN","postgresql://postgres:postgres@localhost:5432/danceapp")

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=DSN, min_size=1, max_size=10)
    return _pool

async def execute(sql: str, *args):
    pool = await get_pool()
    async with pool.acquire() as con:
        return await con.execute(sql, *args)

async def fetchrow(sql: str, *args):
    pool = await get_pool()
    async with pool.acquire() as con:
        return await con.fetchrow(sql, *args)

async def fetch(sql: str, *args):
    pool = await get_pool()
    async with pool.acquire() as con:
        return await con.fetch(sql, *args)
