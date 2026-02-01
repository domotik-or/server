import argparse
import asyncio
import logging
from logging import StreamHandler
import signal
import sys

from aiohttp import web
import aiohttp_jinja2
import aiohttp_cors
import jinja2

import server.config as config
from server.db import close as db_close
from server.db import init as db_init
from server.graph import init as graph_init
from server.serverm import make_app
from server.serverm import close as server_close
from server.serverm import init as server_init
from server.utils import set_loggers_level

logger = logging.getLogger()
stream_handler = StreamHandler(stream=sys.stdout)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


async def init():
    set_loggers_level(config.loggers)

    graph_init()
    await db_init()
    await server_init()


async def close():
    await db_close()
    await server_close()


async def run(config_filename: str):
    config.read(config_filename)

    await init()

    while True:
        await asyncio.sleep(1)


def sigterm_handler(_signo, _stack_frame):
    # raises SystemExit(0):
    sys.exit(0)


app = make_app()


def main():
    signal.signal(signal.SIGTERM, sigterm_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.toml")
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        logger.info("server started")
        loop.run_until_complete(run(args.config))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(close())
        loop.stop()
        logger.info("server stopped")
