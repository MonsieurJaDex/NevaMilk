# core/models.py
from dataclasses import dataclass
from enum import Enum
from core.schema import SensorType, Payload

class ProcessStage(Enum):
    SMOKE_1 = ("Первое копчение", 75.0, 70.0, 80.0)  
    SUSHKA_1 = ("Первая сушка", 55.0, 50.0, 60.0)
    SMOKE_2 = ("Второе копчение", 85.0, 80.0, 90.0)
    SUSHKA_2 = ("Вторая сушка", 40.0, 35.0, 45.0)

    def __init__(self, stage_name, target_temp, min_norm, max_norm):
        self.stage_name = stage_name
        self.target_temp = float(target_temp)
        self.min_norm = float(min_norm)
        self.max_norm = float(max_norm)

@dataclass
class SensorPoint:
    sensor_type: SensorType
    value: float
    unit: str
    min_norm: float | None = None
    max_norm: float | None = None
    is_stabilized: bool = True

    @property
    def is_anomaly(self) -> bool:
        if self.min_norm is None or self.max_norm is None:
            return False
        out_of_range = not (self.min_norm <= self.value <= self.max_norm)
        return out_of_range and self.is_stabilized

    def to_telemetry_payload(self) -> Payload:
        return Payload(category=self.sensor_type, data=float(self.value))

    def to_warning_payload(self) -> Payload:
        sensor_name = str(self.sensor_type)
        if self.value > (self.max_norm or 0):
            return Payload(category=self.sensor_type, data=f"{sensor_name} is too high")
        else:
            return Payload(category=self.sensor_type, data=f"{sensor_name} is too low")