import asyncio
from dataclasses import asdict
from datetime import datetime
import logging
from pathlib import Path
import time

from aiohttp import web
# from aiohttp.web import HTTPOk
# from aiohttp.web import Response
import aiohttp_jinja2
import aiohttp_cors
import jinja2

import server.config as config
from server.graph import plot_pressure
from server.graph import plot_sinsts
from server.graph import plot_temperature_humidity
from server.db import execute_query
from server.typem import ServerError

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_tz = None


def make_app():
    # run a server
    app = web.Application()

    app.router.add_get("/", default_handle)
    app.router.add_get("/set_east", set_east_handle)
    app.router.add_get("/set_event/{name}", set_event_handle)
    app.router.add_get("/set_outdoor", set_outdoor_handle)
    app.router.add_get("/set_sinsts", set_sinsts_handle)
    app.router.add_get("/set_temperature_humidity", set_temperature_humidity_handle)
    app.router.add_get("/datetime", datetime_handle)
    app.router.add_get("/pressure/image", pressure_image_handle)
    app.router.add_get("/sinsts/image", sinsts_image_handle)
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


async def set_east_handle(request: web.Request) -> web.StreamResponse:
    try:
        value = int(request.rel_url.query["value"])
    except KeyError as exc:
        raise web.HTTPBadRequest(reason=f"{exc}")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))

    # store values in db
    await execute_query(
        "INSERT INTO east(value) VALUES (?)",
        value
    )

    data = int(datetime.now().timestamp())
    return web.Response(text=str(data))


async def set_event_handle(request: web.Request) -> web.StreamResponse:
    try:
        name = request.match_info["name"]
    except KeyError as exc:
        raise web.HTTPBadRequest(reason=f"{exc}")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))

    # store values in db
    await execute_query(
        "INSERT INTO event(name) VALUES (?)",
        name
    )

    data = int(datetime.now().timestamp())
    return web.Response(text=str(data))


async def set_outdoor_handle(request: web.Request) -> web.StreamResponse:
    try:
        humidity = int(request.rel_url.query["humidity"])
        temperature = int(request.rel_url.query["temperature"])
        pressure = int(request.rel_url.query["pressure"])
    except KeyError as exc:
        raise web.HTTPBadRequest(reason=f"{exc}")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))

    # store values in db
    await execute_query(
        "INSERT INTO outdoor(temperature, humidity, pressure) VALUES (?, ?, ?)",
        temperature / 100.0, humidity / 100.0, pressure / 100.0
    )

    data = int(datetime.now().timestamp())
    return web.Response(text=str(data))


async def set_sinsts_handle(request: web.Request) -> web.StreamResponse:
    try:
        value = int(request.rel_url.query["value"])
    except KeyError as exc:
        raise web.HTTPBadRequest(reason=f"{exc}")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))

    # store values in db
    await execute_query(
        "INSERT INTO sinsts(value) VALUES (?)",
        value
    )

    data = int(datetime.now().timestamp())
    return web.Response(text=str(data))


async def set_temperature_humidity_handle(request: web.Request) -> web.StreamResponse:
    try:
        device = request.rel_url.query["device"]
        humidity = int(request.rel_url.query["humidity"])
        temperature = int(request.rel_url.query["temperature"])
    except KeyError as exc:
        raise web.HTTPBadRequest(reason=f"{exc}")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))

    # store values in db
    await execute_query(
        "INSERT INTO temperature_humidity(device, humidity, temperature) VALUES (?, ?, ?)",
        device, humidity / 100.0, temperature / 100.0
    )

    data = int(datetime.now().timestamp())
    return web.Response(text=str(data))


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


async def sinsts_image_handle(request: web.Request) -> web.StreamResponse:
    try:
        data = await plot_sinsts()
        return web.Response(body=data, content_type="image/png")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))


async def pressure_image_handle(request: web.Request) -> web.StreamResponse:
    try:
        device = config.atmospheric_pressure
        data = await plot_pressure(device.min, device.max)
        return web.Response(body=data, content_type="image/png")
    except ServerError as exc:
        return web.HTTPInternalServerError(reason=str(exc))


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
