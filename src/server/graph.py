from datetime import datetime
from datetime import timedelta
from io import BytesIO

from dateutil import parser as dateparser
import matplotlib
import matplotlib.style
from matplotlib.figure import Figure

from server.queries import get_all_linky_records
from server.queries import get_all_pressure_records
from server.queries import get_all_sonoff_snzb02p_records


def init():
    matplotlib.set_loglevel("info")


async def plot_pressure_linky():
    matplotlib.style.use("ggplot")

    fig = Figure(figsize=(10, 8))
    plt1, plt2 = fig.subplots(2, 1)

    dts = []
    values = []

    start_datetime = datetime.now() - timedelta(days=2)
    records = await get_all_pressure_records(start_datetime, datetime.now())
    for r in records:
        dts.append(r["timestamp"])
        values.append(r["pressure"])

    plt1.set_title("Pressure")
    plt1.set_ylabel("hPa")
    plt1.plot(dts, values)

    dts = []
    values = []

    start_datetime = datetime.now() - timedelta(days=2)
    records = await get_all_linky_records(start_datetime, datetime.now())
    for r in records:
        dts.append(r["timestamp"])
        values.append(r["sinst"])

    plt2.set_title("Linky")
    plt2.set_ylabel("VA")
    plt2.plot(dts, values)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def plot_snzb02p(device: str):
    fig = Figure(figsize=(10, 8))
    fig.suptitle(device, fontsize=16)
    plt1, plt2 = fig.subplots(2, 1, sharex=True)

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


    plt1.plot(dts, hmds)
    plt1.set_title("Humidity")
    plt1.set_ylabel("%RH")

    plt2.plot(dts, tmps)
    plt2.set_title("Temperature")
    plt2.set_ylabel("°C")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def close():
    pass
