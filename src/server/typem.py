from dataclasses import dataclass
from enum import auto
from enum import Enum


class TriggerType(Enum):
    both = auto()
    raising = auto()
    falling = auto()


@dataclass
class AtmosphericPressureConfig:
    min: float
    max: float


@dataclass
class DatabaseConfig:
    path: str


@dataclass
class EventConfig:
    name: str
    trigger: TriggerType


@dataclass
class GeneralConfig:
    altitude: float
    port: int


@dataclass
class HumidityTemperatureConfig:
    humidity_min: float
    humidity_max: float
    name: str
    temperature_min: float
    temperature_max: float
