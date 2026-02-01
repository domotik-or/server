import asyncio
import importlib
import logging

# logger initial setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def set_loggers_level(config_loggers: dict):
    # set log level of modules logger
    for log in config_loggers:
        module = log["module"]
        level = log["level"]
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            logger.warning(f"module {module} not found")
            continue

        if module in logging.Logger.manager.loggerDict.keys():
            logging.getLogger(module).setLevel(level)
        else:
            raise Exception("incorrect type")
