from dataclasses import dataclass
from enum import auto
from enum import Enum


@dataclass
class AtmosphericPressureConfig:
    altitude: float
    min: float
    max: float


@dataclass
class DatabaseConfig:
    path: str


@dataclass
class EventConfig:
    name: str


@dataclass
class HumidityTemperatureConfig:
    humidity_min: float
    humidity_max: float
    temperature_min: float
    temperature_max: float


@dataclass
class ServerConfig:
    address: str
    port: int


class ServerError(Exception):
    pass
