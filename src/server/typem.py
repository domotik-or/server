from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    path: str


@dataclass
class GeneralConfig:
    altitude: float
    port: int


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
