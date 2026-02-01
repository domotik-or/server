from datetime import datetime
from datetime import timedelta
from io import BytesIO

from dateutil import parser as dateparser
import matplotlib
import matplotlib.dates as mdates
import matplotlib.style
from matplotlib.figure import Figure
import pytz
from qbstyles import mpl_style

import server.config as config
from server.db import get_all_linky_records
from server.db import get_all_pressure_records
from server.db import get_all_temperature_humidity_records


def init():
    matplotlib.set_loglevel("info")
    mpl_style(dark=True)


def set_axis_style(ax):
    ax.tick_params(axis="x", labelsize=12, which="major")
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(3, 24, 3)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(True, which="both")


def _pressure_at_altitude(pressure: float) -> float:
    return pressure * pow(1.0 - config.general.altitude / 44330.0, 5.255)


async def plot_linky(days: int = 2) -> bytes:
    fig = Figure(figsize=(10, 4), constrained_layout=True)
    ax = fig.add_subplot()

    dts = []
    values = []

    start_datetime = datetime.now(pytz.utc) - timedelta(days=days)
    records = await get_all_linky_records(start_datetime, datetime.now(pytz.utc))
    for r in records:
        values.append(r[1])  # sinst
        dts.append(datetime.fromtimestamp(r[2]))  # timestamp

    ax.set_title("Linky")
    ax.set_ylabel("VA")
    set_axis_style(ax)
    ax.plot(dts, values, color="yellow")

    fig.autofmt_xdate(rotation=30, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf.getvalue()


async def plot_pressure(pmin: float, pmax: float, days: int = 3) -> bytes:
    fig = Figure(figsize=(10, 4), constrained_layout=True)
    ax = fig.add_subplot()

    dts = []
    values = []

    start_datetime = datetime.now(pytz.utc) - timedelta(days=days)
    records = await get_all_pressure_records(start_datetime, datetime.now(pytz.utc))
    for r in records:
        values.append(r[0])  # pressure
        dts.append(datetime.fromtimestamp(r[1]))  # timestamp

    ax.set_title("Pressure")
    ax.set_ylabel("hPa")
    ax.set_ylim(
        auto=False,
        ymin=_pressure_at_altitude(pmin),
        ymax=_pressure_at_altitude(pmax)
    )
    set_axis_style(ax)
    ax.axhline(y=_pressure_at_altitude(1013.25), color='w', linestyle=':')
    ax.plot(dts, values, color="limegreen", linewidth=2)

    fig.autofmt_xdate(rotation=60, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf.getvalue()


async def plot_temperature_humidity(
    device: str, hmin: float, hmax: float, tmin: float, tmax: float, days: int = 2
) -> bytes:
    fig = Figure(figsize=(10, 8), constrained_layout=True)
    ax1, ax2 = fig.subplots(2, 1)

    dts = []
    hmds = []
    tmps = []
    start_datetime = datetime.now(pytz.utc) - timedelta(days=days)
    records = await get_all_temperature_humidity_records(
        device, start_datetime, datetime.now(pytz.utc)
    )
    for r in records:
        hmds.append(r[0])  # humidity
        tmps.append(r[1])  # temperature
        dts.append(datetime.fromtimestamp(r[2]))  # timestamp

    ax1.set_title("Humidity")
    ax1.set_ylabel("%RH")
    ax1.set_ylim( auto=False, ymin=hmin, ymax=hmax)
    set_axis_style(ax1)
    ax1.plot(dts, hmds, color="deepskyblue", linewidth=2)

    ax2.set_title("Temperature")
    ax2.set_ylabel("°C")
    set_axis_style(ax2)
    ax2.set_ylim(auto=False, ymin=tmin, ymax=tmax)
    ax2.plot(dts, tmps, color="orange", linewidth=2)

    fig.autofmt_xdate(rotation=30, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf.getvalue()


async def close():
    pass
