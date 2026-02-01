from os import getenv
from pathlib import Path
import sys
import tomllib

from dotenv import load_dotenv

from server.typem import AtmosphericPressureConfig
from server.typem import DatabaseConfig
from server.typem import EventConfig
from server.typem import GeneralConfig
from server.typem import HumidityTemperatureConfig
from server.typem import ServerConfig
from server.typem import TriggerType

database = None
events = []
general = None
humidity_temperatures = {}
loggers = {}
atmospheric_pressure = None
server = None


def read(config_filename: str):
    config_file = Path(config_filename)
    with open(config_file, "rb") as f:
        raw_config = tomllib.load(f)

    global events
    global humidity_temperatures
    global atmospheric_pressure
    devices = raw_config["device"]
    for name, device in devices.items():
        device_type = device.pop("type")
        if device_type == "event":
            device["name"] = name
            try:
                trigger_type = TriggerType[device["trigger"]]
            except KeyError as exc:
                raise Exception(f"unknown trigger type: {trigger_type }") from exc
            events.append(EventConfig(name, trigger_type))
        elif device_type == "temperature-humidity":
            humidity_temperatures[name] = HumidityTemperatureConfig(**device)
        elif device_type == "atmospheric-pressure":
            atmospheric_pressure = AtmosphericPressureConfig(**device)
        else:
            raise Exception(f"unknown type: {device_type}")

    global general
    general = GeneralConfig(**raw_config["general"])

    global database
    database = DatabaseConfig(**raw_config["database"])

    global loggers
    loggers = raw_config["logger"]

    global server
    server = ServerConfig(**raw_config["server"])


if __name__ == "__main__":
    read("config.toml")
