import asyncio
import base64
from dataclasses import asdict
from datetime import datetime
from datetime import timedelta
import logging
from pathlib import Path
import time

from aiohttp import web
# from aiohttp.web import HTTPOk
from aiohttp.web import json_response
# from aiohttp.web import Response
import aiohttp_jinja2
import aiohttp_cors
import jinja2

import server.config as config
from server.graph import plot_linky
from server.graph import plot_pressure
from server.graph import plot_temperature_humidity
from server.db import get_linky_records
from server.db import get_all_on_off_records
from server.db import get_on_off_records
from server.db import get_pressure_records
from server.db import get_temperature_humidity_records
from server.typem import ServerError

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_tz = None


def make_app():
    # run a server
    app = web.Application()

    app.router.add_get("/", default_handle)
    app.router.add_get("/datetime", datetime_handle)
    app.router.add_get("/linky/csv", linky_csv_handle)
    app.router.add_get("/linky/image", linky_image_handle)
    app.router.add_get("/onoff/csv", onoff_csv_handle)
    app.router.add_get("/onoff/json", onoff_json_handle)
    app.router.add_get("/pressure/csv", pressure_csv_handle)
    app.router.add_get("/pressure/image", pressure_image_handle)
    app.router.add_get("/temperature_humidity/csv", temperature_humidity_csv_handle)
    app.router.add_get("/temperature_humidity/image/{name}", temperature_humidity_image_handle)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)

    # configure jinja2
    path = Path(__file__).parents[0]
    template_dir = Path(path, "templates")
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(template_dir)
    )

    return app


async def init():
    app = make_app()
    # app["config"] = config

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.server.port)
    await site.start()

    logger.debug("server started")


async def close():
    pass


@aiohttp_jinja2.template("domotik.html")
async def default_handle(request: web.Request):

    return {
        "server": config.server,
        "indoor_sensors": {
            k: asdict(v)
            for k, v in config.humidity_temperatures.items()
            if k != "outdoor"
        }
    }


def _get_common_parameters(request: web.Request) -> tuple[datetime, datetime]:
    try:
        value = int(request.rel_url.query["start"])
    except KeyError:
        value = 0
    except ValueError:
        raise web.HTTPBadRequest(reason="start: bad parameter")
    start_date = datetime.fromtimestamp(value)

    try:
        value = int(request.rel_url.query["end"])
    except KeyError:
        value = int(time.time())
    except ValueError:
        raise web.HTTPBadRequest(reason="end: bad parameter")
    end_date = datetime.fromtimestamp(value)

    return start_date, end_date


async def datetime_handle(request: web.Request) -> web.Response:
    data = {"value": datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
    return web.json_response(data)


async def linky_image_handle(request: web.Request) -> web.StreamResponse:
    try:
        data = await plot_linky()
        return web.Response(body=data, content_type="image/png")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))


async def linky_csv_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = _get_common_parameters(request)

    filename = f"linky-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f"Attachment; filename={filename}"
        },
    )
    await response.prepare(request)

    # send csv header
    await response.write("timestamp, east, sinst\n".encode())

    async for lks in get_linky_records(start_date, end_date):
        if len(lks) == 0:
            break

        csv = ""
        for lk in lks:
            csv += f"{lk['timestamp']}, {lk['east']}, {lk['sinst']}\n"

        await response.write(csv.encode())

    await response.write_eof()
    return response


async def onoff_csv_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = _get_common_parameters(request)

    filename = f"onoff-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f"Attachment; filename={filename}"
        },
    )
    await response.prepare(request)

    # send csv header
    await response.write("timestamp, device, state\n".encode())

    async for oos in get_on_off_records(start_date, end_date):
        if len(oos) == 0:
            break

        csv = ""
        for oo in oos:
            csv += f"{oo['timestamp']}, {oo['device']}, {oo['state']}\n"

        await response.write(csv.encode())

    await response.write_eof()
    return response


async def onoff_json_handle(request: web.Request) -> web.Response:
    start_datetime = datetime.now() - timedelta(weeks=4)
    data = {}
    for device in config.events:
        name = device.name
        if name not in data:
            data[name] = []
        data[name] += [
            (datetime.fromtimestamp(evt[2]).strftime("%Y/%m/%d %H:%M"))
            for evt in await get_all_on_off_records(
                name, start_datetime, datetime.now()
            )
        ]
    return web.json_response(data)


async def pressure_csv_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = _get_common_parameters(request)

    filename = f"pressure-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f"Attachment; filename={filename}"
        },
    )
    await response.prepare(request)

    # send csv header
    await response.write("timestamp, pressure\n".encode())

    async for prs in get_pressure_records(start_date, end_date):
        if len(prs) == 0:
            break

        csv = ""
        for pr in prs:
            csv += f"{pr['timestamp']}, {pr['pressure']}\n"

        await response.write(csv.encode())

    await response.write_eof()
    return response


async def pressure_image_handle(request: web.Request) -> web.StreamResponse:
    try:
        device = config.atmospheric_pressure
        data = await plot_pressure(device.min, device.max)
        return web.Response(body=data, content_type="image/png")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))


async def temperature_humidity_csv_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = _get_common_parameters(request)
    try:
        name = request.rel_url.query["name"]
    except KeyError:
        raise web.HTTPBadRequest(reason="device: missing parameter")

    filename = f"temperature_humidity-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f"Attachment; filename={filename}"
        },
    )
    await response.prepare(request)

    # send csv header
    await response.write("timestamp, name, humidity, temperature\n".encode())

    async for sss in get_temperature_humidity_records(name, start_date, end_date):
        if len(sss) == 0:
            break

        csv = ""
        for ss in sss:
            csv += f"{ss['timestamp']}, {ss['humidity']}, {ss['temperature']}\n"

        await response.write(csv.encode())

    await response.write_eof()
    return response


async def temperature_humidity_image_handle(request: web.Request) -> web.StreamResponse:
    try:
        name = request.match_info["name"]
    except KeyError:
        raise web.HTTPBadRequest(reason="device: missing parameter")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))

    try:
        device = config.humidity_temperatures[name]
    except KeyError:
        raise web.HTTPBadRequest(reason="device: not found in configuration")

    data = await plot_temperature_humidity(
        name,
        device.humidity_min, device.humidity_max,
        device.temperature_min, device.temperature_max
    )
    return web.Response(body=data, content_type="image/png")


async def run(config_filename: str):
    config.read(config_filename)

    await init()


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
        pass
    finally:
        loop.run_until_complete(close())
        loop.stop()
        print("done")
