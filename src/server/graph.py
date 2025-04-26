from datetime import datetime
from datetime import timedelta
from io import BytesIO

from dateutil import parser as dateparser
import matplotlib
import matplotlib.dates as mdates
import matplotlib.style
from matplotlib.figure import Figure
from qbstyles import mpl_style

import server.config as config
from server.queries import get_all_linky_records
from server.queries import get_all_pressure_records
from server.queries import get_all_sonoff_snzb02p_records



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


async def plot_linky(days: int = 2):
    fig = Figure(figsize=(10, 4), constrained_layout=True)
    ax = fig.add_subplot()

    dts = []
    values = []

    start_datetime = datetime.now() - timedelta(days=days)
    records = await get_all_linky_records(start_datetime, datetime.now())
    for r in records:
        dts.append(r["timestamp"])
        values.append(r["sinst"])

    # ax.set_title("Linky")
    ax.set_ylabel("VA")
    set_axis_style(ax)
    ax.plot(dts, values, color="yellow")

    fig.autofmt_xdate(rotation=30, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def plot_pressure(days: int = 3):
    fig = Figure(figsize=(10, 4), constrained_layout=True)
    ax = fig.add_subplot()

    dts = []
    values = []

    start_datetime = datetime.now() - timedelta(days=days)
    records = await get_all_pressure_records(start_datetime, datetime.now())
    for r in records:
        dts.append(r["timestamp"])
        values.append(r["pressure"])

    # ax.set_title("Pressure")
    ax.set_ylabel("hPa")
    ax.set_ylim(
        auto=False,
        ymin=_pressure_at_altitude(config.graph.pressure_min),
        ymax=_pressure_at_altitude(config.graph.pressure_max)
    )
    set_axis_style(ax)
    ax.plot(dts, values, color="limegreen", linewidth=2)

    fig.autofmt_xdate(rotation=60, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def plot_snzb02p(device: str, days: int = 2):
    fig = Figure(figsize=(10, 8), constrained_layout=True)
    ax1, ax2 = fig.subplots(2, 1)

    dts = []
    hmds = []
    tmps = []
    start_datetime = datetime.now() - timedelta(days=days)
    records = await get_all_sonoff_snzb02p_records(
        device, start_datetime, datetime.now()
    )
    for r in records:
        hmds.append(r["humidity"])
        tmps.append(r["temperature"])
        dts.append(r["timestamp"])


    ax1.set_title("Humidity")
    ax1.set_ylabel("%RH")
    ax1.set_ylim(
        auto=False,
        ymin=config.graph.indoor_hygrometry_min,
        ymax=config.graph.indoor_hygrometry_max
    )
    set_axis_style(ax1)
    ax1.plot(dts, hmds, color="deepskyblue", linewidth=2)

    ax2.set_title("Temperature")
    ax2.set_ylabel("°C")
    set_axis_style(ax2)
    ax2.set_ylim(
        auto=False,
        ymin=config.graph.indoor_temperature_min,
        ymax=config.graph.indoor_temperature_max
    )
    ax2.plot(dts, tmps, color="orange", linewidth=2)

    fig.autofmt_xdate(rotation=30, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def close():
    pass
