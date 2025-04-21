from datetime import datetime
from datetime import timedelta
from io import BytesIO

from dateutil import parser as dateparser
from matplotlib.figure import Figure

from server.query import get_all_linky_records
from server.query import get_all_pressure_records
from server.query import get_all_sonoff_snzb02p_records


async def plot_pressure_linky():
    fig = Figure()
    # fig.style.use("ggplot")

    dts = []
    values = []

    start_datetime = int((datetime.now() - timedelta(days=2)).timestamp())
    await get_all_pressure_records(start_datetime, datetime.now())

    fig.subplot(2, 1, 1, fig_size=(10, 8))
    fig.title("Pression")
    fig.ylabel("hPa")
    fig.plot(dts, values)

    dts = []
    values = []

    start_datetime = int((datetime.now() - timedelta(days=2)).timestamp())
    await get_all_linky_records(start_datetime, datetime.now())

    fig.subplot(2, 1, 2)
    fig.title("Linky")
    fig.ylabel("VA")
    fig.plot(dts, values)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


# for n, device in enumerate(config.device.snzb02p):
async def plot_snzb02p(device: str):
    fig = Figure()

    dts = []
    hmds = []
    tmps = []
    start_datetime = int((datetime.now() - timedelta(days=2)).timestamp())
    await get_all_sonoff_snzb02p_records(device, start_datetime, datetime.now())

    fig_, (ax1, ax2) = fig.subplots(2, 1, sharex=True, fig_size=(10, 8))
    fig_.suptitle(device, fontsize=16)

    ax1.plot(dts, hmds)
    ax1.set_title("Humidity")
    ax1.set_ylabel("%RH")

    ax2.plot(dts, tmps)
    ax2.set_title("Temperature")
    ax2.set_ylabel("°C")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    return buf


async def close():
    pass
