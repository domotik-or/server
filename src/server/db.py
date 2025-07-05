import asyncio
from datetime import datetime
from datetime import timedelta
import logging
from typing import AsyncGenerator
from typing import Optional

import aiosqlite
from sqlite3 import Error as Sqlite3Error
from sqlite3 import Row

import server.config as config

_conn = None

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def init():
    global _conn

    try:
        _conn = await aiosqlite.connect(config.database.path, autocommit=True)
    except Sqlite3Error as exc:
        logger.error(f"error while creating tables ({exc})")


async def get_rows(query: str, *args) -> Optional[list[Row]]:
    if _conn is not None:
        cur = await _conn.execute(query, args)
        return await cur.fetchall()
    return None


async def get_many_rows(
    query: str, *args, records_number: int = 100
) -> AsyncGenerator[list[Row], None]:
    try:
        cur = await _conn.execute(query, args)
    except Sqlite3Error as exc:
        logger.error(f"error while executing query ({exc})")
        return
    while True:
        records = await cur.fetchmany(records_number)
        if len(records) == 0:
            break
        yield records


async def execute_query(query: str, *args):
    if _conn is not None:
        try:
            await _conn.execute(query, args)
        except Sqlite3Error as exc:
            logger.error(f"error while executing query ({exc})")


async def close():
    global _conn

    if _conn is not None:
        await _conn.close()
        _conn = None


_linky_query = (
    "SELECT * FROM linky "
    "WHERE timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_all_linky_records(
    start_date: datetime, end_date: datetime
):
    """Get the linky data from the linky table"""
    return await get_rows(_linky_query, start_date, end_date)


async def get_linky_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the linky data from the linky table"""
    async for sss in get_many_rows(_linky_query, start_date, end_date):
        yield sss


_on_off_query = (
    "SELECT * FROM on_off "
    "WHERE device=$1 AND timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_all_on_off_records(
    device: str, start_date: datetime, end_date: datetime
):
    """Get the on_off data from the on_off table"""
    return await get_rows(_on_off_query, device, start_date, end_date)


async def get_on_off_records(
    device: str, start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the on_off data from the on_off table"""
    async for sss in get_many_rows(_snzb02p_query, device, start_date, end_date):
        yield sss


_pressure_query = (
    "SELECT * FROM pressure "
    "WHERE timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_all_pressure_records(
    start_date: datetime, end_date: datetime
):
    """Get the pressure data from the pressure table"""
    return await get_rows(_pressure_query, start_date, end_date)


async def get_pressure_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the pressure data from the pressure table"""
    async for prs in get_many_rows(_pressure_query, start_date, end_date):
        yield sss


_snzb02p_query = (
    "SELECT timestamp, humidity, temperature FROM sonoff_snzb02p "
    "WHERE device=$1 AND timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_all_sonoff_snzb02p_records(
    device: str, start_date: datetime, end_date: datetime
):
    """Get the snzb02p data from the sonoff_snzb02p table"""
    return await get_rows(_snzb02p_query, device, start_date, end_date)


async def get_sonoff_snzb02p_records(
    device: str, start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the snzb02p data from the sonoff_snzb02p table"""
    async for sss in get_many_rows(_snzb02p_query, device, start_date, end_date):
        yield sss


async def run(config_filename: str):
    config.read(config_filename)

    await init()

    try:
        # await execute_query(
        #     "INSERT INTO on_off(device, state) VALUES (?, ?)", "doorbell", True
        # )
        #
        # await execute_query(
        #     "INSERT INTO linky(east, sinst) VALUES (?, ?)", 1000, 2000
        # )
        #
        # await execute_query(
        #     "INSERT INTO pressure(pressure) VALUES (?)", 1013.25
        # )
        #
        # await execute_query(
        #     "INSERT INTO sonoff_snzb02p(device, humidity, temperature) VALUES (?, ?, ?)",
        #     "sejour", 50.0, 21.0
        # )

        rows = await get_all_linky_records(datetime.now() - timedelta(days=5), datetime.now())
        print(rows)

        async for row in get_linky_records(datetime.now() - timedelta(days=5), datetime.now()):
            print(row)

    finally:
        await close()


if __name__ == "__main__":
    import argparse
    import sys

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(module)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.toml")
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run(args.config))
    except KeyboardInterrupt:
        loop.run_until_complete(close())
        loop.stop()
    finally:
        print("done")
