from datetime import datetime
import logging
from typing import AsyncGenerator

from db import attach_db
from db import close_db
from db import get_many_rows

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
        "WHERE date_time >= $1 AND date_time <= $2;"
    )
    async for lks in get_many_rows(query, start_date, end_date):
        yield [dict(e) for e in lks]


async def get_onoff_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the on_off data from the on_off table"""
    query = (
        "SELECT * FROM on_off "
        "WHERE date_time >= $1 AND date_time <= $2;"
    )
    async for oos in get_many_rows(query, start_date, end_date):
        yield [dict(e) for e in oos]


async def get_pressure_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the pressure data from the pressure table"""
    query = (
        "SELECT * FROM pressure "
        "WHERE date_time >= $1 AND date_time <= $2;"
    )
    async for prs in get_many_rows(query, start_date, end_date):
        yield [dict(e) for e in prs]


async def get_sonoff_snzb02p_records(
    start_date: datetime, end_date: datetime
) -> AsyncGenerator[list[dict], None]:
    """Get the snzb02p data from the sonoff_snzb02p table"""
    query = (
        "SELECT * FROM sonoff_snz02p "
        "WHERE date_time >= $1 AND date_time <= $2;"
    )
    async for lks in get_many_rows(query, start_date, end_date):
        yield [dict(e) for e in lks]
