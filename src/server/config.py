import logging
from os import getenv
from pathlib import Path
import sys
import tomllib

from dotenv import load_dotenv

from server.typem import DeviceConfig
from server.typem import GeneralConfig
from server.typem import LoggerConfig
from server.typem import PostgresqlConfig
from server.typem import SecretsConfig
from server.typem import TcpIpConfig

device = None
general = None
loggers = {}
postgresql = None
secrets = None
tcp_ip = None


def read(config_filename: str):
    config_file = Path(config_filename)
    with open(config_file, "rb") as f:
        raw_config = tomllib.load(f)

    global device
    device = DeviceConfig()
    for k, v in raw_config["device"].items():
        setattr(device, k, v)

    global general
    general = GeneralConfig(**raw_config["general"])

    global postgresql
    postgresql = PostgresqlConfig(**raw_config["postgresql"])

    global loggers
    for lg in raw_config["logger"]:
        level_str = raw_config["logger"][lg]
        level = getattr(logging, level_str)
        loggers[lg] = LoggerConfig(level)

    global tcp_ip
    tcp_ip = TcpIpConfig(**raw_config["tcp-ip"])

    # store secrets in memory
    global secrets
    load_dotenv(general.dotenv_filename)
    secrets = SecretsConfig()
    for v in ("PGPASSWORD",):
        value = getenv(v)
        if value is None:
            sys.stderr.write(f"Missing environment variables {v}\n")
        setattr(secrets, v.lower(), value)
