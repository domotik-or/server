#!/usr/bin/env python3

from datetime import datetime
import importlib
import logging
from logging import StreamHandler
# from pathlib import Path
import signal
import sys
import time

from aiohttp import web
import aiohttp_cors

import config
from queries import close as close_db
from queries import init as init_db
from queries import get_linky_records
from queries import get_onoff_records
from queries import get_pressure_records
from queries import get_sonoff_snzb02p_records

logger = logging.getLogger()
stream_handler = StreamHandler(stream=sys.stdout)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


async def default_handle(request: web.Request) -> web.Response:
    return web.HTTPOk()


def get_common_parameters(request: web.Request) -> tuple[datetime, datetime]:
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


async def linky_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = get_common_parameters(request)

    filename = f"linky-{datetime.now().strftime("%Y%m%d%H%M%S")}.csv"
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


async def onoff_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = get_common_parameters(request)

    filename = f"onoff-{datetime.now().strftime("%Y%m%d%H%M%S")}.csv"
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

    async for oos in get_onoff_records(start_date, end_date):
        if len(oos) == 0:
            break

        csv = ""
        for oo in oos:
            csv += f"{oo['timestamp']}, {oo['device']}, {oo['state']}\n"

        await response.write(csv.encode())

    await response.write_eof()
    return response


async def pressure_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = get_common_parameters(request)

    filename = f"linky-{datetime.now().strftime("%Y%m%d%H%M%S")}.csv"
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


async def sonoff_snzb02p_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = get_common_parameters(request)

    filename = f"linky-{datetime.now().strftime("%Y%m%d%H%M%S")}.csv"
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

    async for sss in get_sonoff_snzb02p_records(start_date, end_date):
        if len(sss) == 0:
            break

        csv = ""
        for ss in sss:
            csv += f"{ss['timestamp']}, {ss['east']}, {ss['sinst']}\n"

        await response.write(csv.encode())

    await response.write_eof()
    return response


async def init():
    # set log level of modules logger
    for lg_name, lg_config in config.loggers.items():
        try:
            importlib.import_module(lg_name)
        except ModuleNotFoundError:
            logger.warning(f"module {lg_name} not found")
            continue

        if lg_name in logging.Logger.manager.loggerDict.keys():
            logging.getLogger(lg_name).setLevel(lg_config.level)


async def startup(app):
    await init_db()

    # setup_security(
    #     app,
    #     SessionIdentityPolicy(),
    #     DBAuthorizationPolicy(db_pool)
    # )


async def cleanup(app):
    close_db()


async def make_app():
    # run a server
    app = web.Application()

    app.router.add_get("/", default_handle)
    app.router.add_get("/linky", linky_handle)
    app.router.add_get("/onoff", onoff_handle)
    app.router.add_get("/pressure", pressure_handle)
    app.router.add_get("/snzb02p", sonoff_snzb02p_handle)

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

    # path = Path(__file__).parents[0]
    # template_dir = Path(path, "templates")
    # aiohttp_jinja2.setup(
    #     app,
    #     loader=FileSystemLoader(template_dir),
    # )

    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)

    return app


def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)


config.read("config.toml")
app = make_app()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigterm_handler)

    web.run_app(
        app,
        host=app["config"]["http_server"]["host"],
        port=int(app["config"]["http_server"]["port"])
    )
