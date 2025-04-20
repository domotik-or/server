from datetime import datetime
import logging
from typing import AsyncGenerator

from server.db import attach_db
from server.db import close_db
from server.db import get_many_rows

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def init():
    await attach_db()


async def close():
    await close_db()


async def get_linky_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the linky data from the linky table"""
    query = (
        "SELECT * FROM linky "
        "WHERE timestamp >= $1 AND timestamp <= $2 "
        "ORDER BY timestamp;"
    )
    async for sss in get_many_rows(query, start_date, end_date):
        yield [dict(e) for e in sss]


async def get_onoff_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the on_off data from the on_off table"""
    query = (
        "SELECT * FROM on_off "
        "WHERE timestamp >= $1 AND timestamp <= $2 "
        "ORDER BY timestamp;"
    )
    async for oos in get_many_rows(query, start_date, end_date):
        yield [dict(e) for e in oos]


async def get_pressure_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the pressure data from the pressure table"""
    query = (
        "SELECT * FROM pressure "
        "WHERE timestamp >= $1 AND timestamp <= $2 "
        "ORDER BY timestamp;"
    )
    async for prs in get_many_rows(query, start_date, end_date):
        yield [dict(e) for e in prs]


async def get_sonoff_snzb02p_records(
    device: str, start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the snzb02p data from the sonoff_snzb02p table"""
    query = (
        "SELECT timestamp, humidity, temperature FROM sonoff_snzb02p "
        "WHERE device=$1 AND timestamp >= $2 AND timestamp <= $3 "
        "ORDER BY timestamp;"
    )
    async for sss in get_many_rows(query, device, start_date, end_date):
        yield [dict(e) for e in sss]
