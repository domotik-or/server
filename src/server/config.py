from pathlib import Path
import tomllib

from server.typem import AtmosphericPressureConfig
from server.typem import DatabaseConfig
from server.typem import EventConfig
from server.typem import HumidityTemperatureConfig
from server.typem import ServerConfig
from server.typem import TriggerType

atmospheric_pressure = None
database = None
events = []
general = None
humidity_temperatures = {}
loggers = {}
server = None


def read(config_filename: str):
    config_file = Path(config_filename)
    with open(config_file, "rb") as f:
        raw_config = tomllib.load(f)

    global events  # noqa
    global humidity_temperatures  # noqa
    global atmospheric_pressure
    devices = raw_config["device"]
    for name, device in devices.items():
        device_type = device.pop("type")
        if device_type == "event":
            device["name"] = name
            try:
                trigger_type = TriggerType[device["trigger"]]
            except KeyError as exc:
                raise Exception(f"unknown trigger type: {trigger_type}") from exc
            events.append(EventConfig(name, trigger_type))
        elif device_type == "temperature-humidity":
            humidity_temperatures[name] = HumidityTemperatureConfig(**device)
        elif device_type == "atmospheric-pressure":
            atmospheric_pressure = AtmosphericPressureConfig(**device)
        else:
            raise Exception(f"unknown type: {device_type}")

    global database
    database = DatabaseConfig(**raw_config["database"])

    global loggers
    loggers = raw_config["logger"]

    global server
    server = ServerConfig(**raw_config["server"])


if __name__ == "__main__":
    read("config.toml")
