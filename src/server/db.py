import asyncio
from datetime import datetime
from datetime import timedelta
import logging
from typing import Optional

import aiosqlite
from sqlite3 import Error as Sqlite3Error
from sqlite3 import Row

import server.config as config

_conn = None

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def create_tables():
    await _conn.execute(
        "CREATE TABLE IF NOT EXISTS east ("
        "    value INTEGER,"
        "    timestamp TIMESTAMP(1) DEFAULT (STRFTIME('%s', 'NOW'))"
        ");"
    )

    await _conn.execute(
        "CREATE TABLE IF NOT EXISTS event ("
        "    name VARCHAR(30),"
        "    timestamp TIMESTAMP(1) DEFAULT (STRFTIME('%s', 'NOW'))"
        ");"
    )

    await _conn.execute(
        "CREATE TABLE IF NOT EXISTS sinsts ("
        "    value INTEGER,"
        "    timestamp TIMESTAMP(1) DEFAULT (STRFTIME('%s', 'NOW'))"
        ");"
    )

    await _conn.execute(
        "CREATE TABLE IF NOT EXISTS outdoor ("
        "    humidity REAL,"
        "    pressure REAL,"
        "    temperature REAL,"
        "    timestamp TIMESTAMP(1) DEFAULT (STRFTIME('%s', 'NOW'))"
        ");"
    )

    await _conn.execute(
        "CREATE TABLE IF NOT EXISTS temperature_humidity ("
        "    device VARCHAR(30),"
        "    humidity REAL,"
        "    temperature REAL,"
        "    timestamp TIMESTAMP(1) DEFAULT (STRFTIME('%s', 'NOW'))"
        ");"
    )


async def init():
    global _conn

    try:
        _conn = await aiosqlite.connect(config.database.path, autocommit=True)
        await create_tables()
    except Sqlite3Error as exc:
        logger.error(f"error while creating tables ({exc})")


async def get_rows(query: str, *args) -> Optional[list[Row]]:
    if _conn is not None:
        cur = await _conn.execute(query, args)
        return await cur.fetchall()
    return None


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


_sinsts_query = (
    "SELECT * FROM sinsts "
    "WHERE timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_sinsts_records(
    start_date: datetime, end_date: datetime
) -> Optional[list[Row]]:
    """Get the linky data from the linky table"""
    return await get_rows(
        _sinsts_query, int(start_date.timestamp()), int(end_date.timestamp())
    )


_event_query = (
    "SELECT * FROM event "
    "WHERE device=$1 AND timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_event_records(
    event: str, start_date: datetime, end_date: datetime
) -> Optional[list[Row]]:
    """Get the event data from the event table"""
    return await get_rows(
        _event_query, device,
        int(start_date.timestamp()), int(end_date.timestamp())
    )


_pressure_query = (
    "SELECT * FROM outdoor "
    "WHERE timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_pressure_records(
    start_date: datetime, end_date: datetime
) -> Optional[list[Row]]:
    """Get the pressure data from the outdoor table"""
    return await get_rows(
        _pressure_query, int(start_date.timestamp()), int(end_date.timestamp())
    )


_temperature_humidity_query = (
    "SELECT humidity, temperature, timestamp FROM temperature_humidity "
    "WHERE device=? AND timestamp >= ? AND timestamp <= ? "
    "ORDER BY timestamp;"
)


async def get_temperature_humidity_records(
    device: str, start_date: datetime, end_date: datetime
) -> Optional[list[Row]]:
    """Get the data from the temperature_humidity table"""
    return await get_rows(
        _temperature_humidity_query, device,
        int(start_date.timestamp()), int(end_date.timestamp())
    )


async def run(config_filename: str):
    import pytz

    config.read(config_filename)

    await init()

    try:
        # await execute_query(
        #     "INSERT INTO event(device, state) VALUES (?, ?)", "doorbell", True
        # )
        #
        # await execute_query(
        #     "INSERT INTO pressure(pressure) VALUES (?)", 1013.25
        # )
        #
        # await execute_query(
        #     "INSERT INTO temperature_humidity(device, humidity, temperature) VALUES (?, ?, ?)",
        #     "sejour", 50.0, 21.0
        # )
        await execute_query("DELETE FROM sinsts")
        await execute_query(
            "INSERT INTO sinsts(value) VALUES (?)", 1000
        )
        timestamp = datetime.now(pytz.utc)

        rows = await get_insts_records(timestamp - timedelta(hours=1), timestamp)
        print(rows)
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
