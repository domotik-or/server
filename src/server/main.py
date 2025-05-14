import base64
from datetime import datetime
from datetime import timedelta
import importlib
import logging
from logging import StreamHandler
from pathlib import Path
import signal
import sys
import time

from aiohttp import web
import aiohttp_jinja2
import aiohttp_cors
import jinja2

import server.config as config
from server.graph import init as init_graph
from server.graph import plot_linky
from server.graph import plot_pressure
from server.graph import plot_snzb02p
from server.queries import close as close_db
from server.queries import init as init_db
from server.queries import get_linky_records
from server.queries import get_all_on_off_records
from server.queries import get_on_off_records
from server.queries import get_pressure_records
from server.queries import get_sonoff_snzb02p_records

logger = logging.getLogger()
stream_handler = StreamHandler(stream=sys.stdout)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


@aiohttp_jinja2.template("domotik.html")
async def default_handle(request: web.Request):
    tmpl_context = {
        "datetime": datetime.now(),
        "events": {},
        "images": {}
    }

    # images

    # pressure and linky
    buf_linky = await plot_linky()
    tmpl_context["images"]["linky"] = base64.b64encode(buf_linky.getbuffer()).decode("ascii")
    buf_pressure = await plot_pressure()
    tmpl_context["images"]["pressure"] = base64.b64encode(buf_pressure.getbuffer()).decode("ascii")

    # sonoff snzb02p
    for device in config.devices["snzb02p"]:
        buf = await plot_snzb02p(device)
        tmpl_context["images"][device] = base64.b64encode(buf.getbuffer()).decode("ascii")

    # events

    start_datetime = datetime.now() - timedelta(weeks=4)
    for events in config.devices["events"]:
        tmpl_context["events"][events] = await get_all_on_off_records(
            events, start_datetime, datetime.now()
        )

    return tmpl_context


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


async def onoff_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = get_common_parameters(request)

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


async def pressure_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = get_common_parameters(request)

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


async def sonoff_snzb02p_handle(request: web.Request) -> web.StreamResponse:
    start_date, end_date = get_common_parameters(request)
    try:
        device = request.rel_url.query["device"]
    except KeyError:
        raise web.HTTPBadRequest(reason="device: missing parameter")

    filename = f"snzb02p-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
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
    await response.write("timestamp, device, humidity, temperature\n".encode())

    async for sss in get_sonoff_snzb02p_records(device, start_date, end_date):
        if len(sss) == 0:
            break

        csv = ""
        for ss in sss:
            csv += f"{ss['timestamp']}, {ss['humidity']}, {ss['temperature']}\n"

        await response.write(csv.encode())

    await response.write_eof()
    return response


def _set_loggers_level(config_loggers: dict, module_path: list):
    # set log level of modules logger
    for lg_name, lg_config in config_loggers.items():
        if isinstance(lg_config, dict):
            module_path.append(lg_name)
            _set_loggers_level(lg_config, module_path)
        elif isinstance(lg_config, str):
            this_module_path = '.'.join(module_path + [lg_name])
            try:
                importlib.import_module(this_module_path)
            except ModuleNotFoundError:
                logger.warning(f"module {this_module_path} not found")
                continue

            level = getattr(logging, lg_config)
            if this_module_path in logging.Logger.manager.loggerDict.keys():
                logging.getLogger(this_module_path).setLevel(level)
        else:
            raise Exception("incorrect type")


async def init():
    _set_loggers_level(config.loggers, [])


async def startup(app):
    init_graph()
    await init_db()

    # setup_security(
    #     app,
    #     SessionIdentityPolicy(),
    #     DBAuthorizationPolicy(db_pool)
    # )


async def cleanup(app):
    await close_db()


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

    # configure jinja2
    path = Path(__file__).parents[0]
    template_dir = Path(path, "templates")
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(template_dir)
    )

    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)

    return app


def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)


config.read("/home/domotik/.config/domotik/server.toml")
app = make_app()


def main():
    signal.signal(signal.SIGTERM, sigterm_handler)

    web.run_app(
        app,
        host="0.0.0.0",
        port=config.tcp_ip.port
    )
