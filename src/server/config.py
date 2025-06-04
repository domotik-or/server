import logging
from os import getenv
from pathlib import Path
import sys
import tomllib

from dotenv import load_dotenv

from server.typem import GeneralConfig
from server.typem import GraphConfig
from server.typem import PostgresqlConfig
from server.typem import SecretConfig
from server.typem import TcpIpConfig

devices = None
general = None
graph = None
loggers = {}
postgresql = None
secret = None
tcp_ip = None


def read(config_filename: str):
    config_file = Path(config_filename)
    with open(config_file, "rb") as f:
        raw_config = tomllib.load(f)

    global devices
    devices = raw_config["devices"]

    global general
    general = GeneralConfig(**raw_config["general"])

    global graph
    graph = GraphConfig(**raw_config["graph"])

    global postgresql
    postgresql = PostgresqlConfig(**raw_config["postgresql"])

    global loggers
    loggers = raw_config["logger"]

    global tcp_ip
    tcp_ip = TcpIpConfig(**raw_config["tcp-ip"])

    # store secrets data in config class
    global secret
    load_dotenv(raw_config["secret"]["env_path"])
    secret = SecretConfig()
    for v in raw_config["secret"]["env_names"]:
        value = getenv(v)
        if value is None:
            # not logging system configured yet!
            sys.stderr.write(f"Missing environment variables {v}\n")
        setattr(secret, v.lower(), value)


if __name__ == "__main__":
    read("config.toml")
