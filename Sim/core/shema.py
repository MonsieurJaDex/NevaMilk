# core/schema.py
from __future__ import annotations
import base64
import json
import uuid
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Generic, TypeVar, Union

class SensorType(IntEnum):
    """Тип датчика. Совместимо с Go (iota)."""
    label: str

    def __new__(cls, value: int, label: str) -> "SensorType":
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    UNKNOWN = (0, "unknown")
    TEMPERATURE = (1, "temperature")
    HUMIDITY = (2, "humidity")
    PH = (3, "ph")
    PRESSURE = (4, "pressure")

    def __str__(self) -> str:
        return self.label

    @classmethod
    def from_string(cls, s: str) -> "SensorType":
        for member in cls:
            if member.label == s:
                return member
        raise ValueError(f"unknown sensor type string: {s!r}")


T = TypeVar("T")

@dataclass(frozen=True, slots=True)
class Payload(Generic[T]):
    """
    T может быть:
    - dict (для телеметрии с графиками)
    - str (для warning/alert сообщений)
    """
    category: SensorType
    data: T

    def to_dict(self) -> dict[str, Any]:
        return {"category": str(self.category), "data": self.data}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(',', ':'))

    @classmethod
    def from_json(cls, s: str) -> "Payload[Any]":
        d = json.loads(s)
        return cls(category=SensorType.from_string(d["category"]), data=d["data"])


@dataclass(frozen=True, slots=True)
class MqttMessage:
    device_id: str       # UUID устройства
    payload: str         # Формат: uuid.base64(json_payload)

    @classmethod
    def from_payload(cls, device_id: str, payload: Payload[Any]) -> "MqttMessage":
        """Создаёт сообщение: uuid.base64(json_payload)"""
        payload_json = payload.to_json()
        payload_b64 = base64.b64encode(payload_json.encode("utf-8")).decode("ascii")
        encoded = f"{device_id}.{payload_b64}"
        
        return cls(device_id=device_id, payload=encoded)

    def to_bytes(self) -> bytes:
        return self.payload.encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "MqttMessage":
        encoded = raw.decode("utf-8")
        parts = encoded.split(".", 1)
        if len(parts) != 2:
            raise ValueError("Invalid message format")
        
        return cls(device_id=parts[0], payload=encoded)

    def decode_payload(self) -> Payload[Any]:
        parts = self.payload.split(".", 1)
        if len(parts) != 2:
            raise ValueError("Invalid message format")
        
        payload_json = base64.b64decode(parts[1]).decode("utf-8")
        return Payload.from_json(payload_json)

    @staticmethod
    def generate_device_id() -> str:
        """Генерирует новый UUID v4"""
        return str(uuid.uuid4())
    #enum с типами датчиков
    '''const (
SensorUnknown SensorType = iota
SensorPt100 // Игольчатый датчик Pt100
SensorPt1000 // RTD-зонд Pt1000
SensorPH // pH-датчик
SensorHumidityCap // Ёмкостный датчик влажности
SensorPsychrometric // Психрометрический датчик
SensorLoadCell // Тензодатчик
SensorLevelCap // Ёмкостный сигнализатор уровня
SensorComputerVision // Промышленная камера машинного зрения
SensorClimate // RFID-сенсор температуры и влажности
SensorVibration // Сенсор вибраций
)'''