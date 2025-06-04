from dataclasses import dataclass
from enum import IntEnum


class BatteryEvent(IntEnum):
    CHARGE_20 = 0
    CHARGE_50 = 1


@dataclass
class GeneralConfig:
    altitude: float


@dataclass
class PostgresqlConfig:
    hostname: str
    port: int
    username: str
    databasename: str


@dataclass
class GraphConfig:
    pressure_min: float
    pressure_max: float
    indoor_temperature_min: float
    indoor_temperature_max: float
    indoor_hygrometry_min: float
    indoor_hygrometry_max: float


class SecretConfig:
    pass


@dataclass
class TcpIpConfig:
    port: int
