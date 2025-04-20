from dataclasses import dataclass
from enum import IntEnum


class BatteryEvent(IntEnum):
    CHARGE_20 = 0
    CHARGE_50 = 1


@dataclass
class PostgresqlConfig:
    hostname: str
    port: int
    username: str
    databasename: str


@dataclass
class GeneralConfig:
    dotenv_filename: str


@dataclass
class LoggerConfig:
    level: int


class SecretsConfig:
    pass


@dataclass
class TcpIpConfig:
    port: int
