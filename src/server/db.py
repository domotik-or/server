import logging
from typing import AsyncGenerator

from asyncpg import create_pool
from asyncpg import Record

import server.config as config

_db_pool = None

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def attach_db():
    global _db_pool

    if _db_pool is None:
        dsn = (
            f"postgres://{config.postgresql.username}:{config.secrets.pgpassword}"
            f"@{config.postgresql.hostname}:{config.postgresql.port}/{config.postgresql.databasename}"
        )
        _db_pool = await create_pool(dsn=dsn)


async def get_rows(query: str, *args):
    if _db_pool is not None:
        async with _db_pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetch(query, *args)


async def get_many_rows(query: str, *args, records_number: int = 100) -> AsyncGenerator[list[Record], None]:
    async with _db_pool.acquire() as conn:  # type: ignore[union-attr]
        async with conn.transaction():
            cursor = await conn.cursor(query, *args)
            while True:
                records = await cursor.fetch(records_number)
                yield records


async def execute_query(query: str, *args):
    if _db_pool is not None:
        async with _db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query, *args)


async def close_db():
    global _db_pool

    if _db_pool is not None:
        await _db_pool.close()
        _db_pool = None
