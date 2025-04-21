from datetime import datetime
import logging
from typing import AsyncGenerator

from server.db import attach_db
from server.db import close_db
from server.db import get_many_rows
from server.db import get_rows

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def init():
    await attach_db()


async def close():
    await close_db()


_linky_query = (
    "SELECT * FROM linky "
    "WHERE timestamp >= $1 AND timestamp <= $2 "
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
        yield [dict(e) for e in sss]


_onoff_query = (
    "SELECT * FROM on_off "
    "WHERE timestamp >= $1 AND timestamp <= $2 "
    "ORDER BY timestamp;"
)


async def get_all_onoff_records(
    start_date: datetime, end_date: datetime
):
    """Get the on_off data from the on_off table"""
    return await get_rows(_onoff_query, start_date, end_date)


async def get_onoff_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the on_off data from the on_off table"""
    async for oos in get_many_rows(_onoff_query, start_date, end_date):
        yield [dict(e) for e in oos]


_pressure_query = (
    "SELECT * FROM pressure "
    "WHERE timestamp >= $1 AND timestamp <= $2 "
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
        yield [dict(e) for e in prs]


_snzb02p_query = (
    "SELECT timestamp, humidity, temperature FROM sonoff_snzb02p "
    "WHERE device=$1 AND timestamp >= $2 AND timestamp <= $3 "
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
        yield [dict(e) for e in sss]
