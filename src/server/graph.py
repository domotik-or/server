from datetime import datetime
from datetime import timedelta
from io import BytesIO

from dateutil import parser as dateparser
import matplotlib
import matplotlib.dates as mdates
import matplotlib.style
from matplotlib.figure import Figure

from server.queries import get_all_linky_records
from server.queries import get_all_pressure_records
from server.queries import get_all_sonoff_snzb02p_records


def init():
    matplotlib.set_loglevel("info")


def set_axis_style(ax):
    ax.tick_params(axis="x", labelsize=12, which="major")
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(3, 24, 3)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(True, which="both")


async def plot_pressure_linky():
    matplotlib.style.use("ggplot")

    fig = Figure(figsize=(10, 8), constrained_layout=True)
    ax1, ax2 = fig.subplots(2, 1)

    dts = []
    values = []

    start_datetime = datetime.now() - timedelta(days=2)
    records = await get_all_pressure_records(start_datetime, datetime.now())
    for r in records:
        dts.append(r["timestamp"])
        values.append(r["pressure"])

    ax1.set_title("Pressure")
    ax1.set_ylabel("hPa")
    set_axis_style(ax1)
    ax1.plot(dts, values)

    dts = []
    values = []

    start_datetime = datetime.now() - timedelta(days=2)
    records = await get_all_linky_records(start_datetime, datetime.now())
    for r in records:
        dts.append(r["timestamp"])
        values.append(r["sinst"])

    ax2.set_title("Linky")
    ax2.set_ylabel("VA")
    set_axis_style(ax2)
    ax2.plot(dts, values)

    fig.autofmt_xdate(rotation=30, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def plot_snzb02p(device: str):
    fig = Figure(figsize=(10, 8))
    fig.suptitle(device, fontsize=16)
    ax1, ax2 = fig.subplots(2, 1, sharex=True)

    dts = []
    hmds = []
    tmps = []
    start_datetime = datetime.now() - timedelta(days=2)
    records = await get_all_sonoff_snzb02p_records(
        device, start_datetime, datetime.now()
    )
    for r in records:
        hmds.append(r["humidity"])
        tmps.append(r["temperature"])
        dts.append(r["timestamp"])


    ax1.plot(dts, hmds)
    ax1.set_title("Humidity")
    ax1.set_ylabel("%RH")
    set_axis_style(ax1)

    ax2.plot(dts, tmps)
    ax2.set_title("Temperature")
    ax2.set_ylabel("°C")
    set_axis_style(ax2)

    fig.autofmt_xdate(rotation=30, ha="right", which="both")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def close():
    pass
