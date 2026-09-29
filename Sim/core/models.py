# core/models.py
from dataclasses import dataclass
from enum import Enum
from core.shema import SensorType, Payload

class ProcessStage(Enum):
    SMOKE_1 = ("Первое копчение", 75.0, 70.0, 80.0)  
    SUSHKA_1 = ("Первая сушка", 55.0, 50.0, 60.0)
    SMOKE_2 = ("Второе копчение", 85.0, 80.0, 90.0)
    SUSHKA_2 = ("Вторая сушка", 40.0, 35.0, 45.0)

    def __init__(self, stage_name, target_temp, min_norm, max_norm):
        self.stage_name = stage_name
        self.target_temp = target_temp
        self.min_norm = min_norm
        self.max_norm = max_norm

@dataclass
class TelemetryPoint:
    temperature: float
    min_norm: float
    max_norm: float
    is_stabilized: bool = False

    @property
    def is_anomaly(self) -> bool:
        """Аномалия = вне нормы И после стабилизации"""
        out_of_range = not (self.min_norm <= self.temperature <= self.max_norm)
        return out_of_range and self.is_stabilized

    def to_telemetry_payload(self) -> Payload[dict]:
        """Только температура для графиков"""
        return Payload(
            category=SensorType.TEMPERATURE,
            data={
                "temperature": self.temperature
            }
        )

    def to_warning_payload(self) -> Payload[str]:
        """Строка с сообщением об отклонении"""
        if self.temperature > self.max_norm:
            return Payload(
                category=SensorType.TEMPERATURE,
                data="temperature is too high"
            )
        else:
            return Payload(
                category=SensorType.TEMPERATURE,
                data="temperature is too low"
            )