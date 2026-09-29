# core/schema.py
from __future__ import annotations
import base64
import json
import uuid
from dataclasses import dataclass
from enum import IntEnum
from typing import Union

class SensorType(IntEnum):
    """Типы датчиков — СТРОГО как в Go-коде"""
    
    UNKNOWN = (0, "unknown")
    TEMPERATURE = (1, "temperature")
    HUMIDITY = (2, "humidity")
    PH = (3, "pH Sensor")        # ← БЫЛО "ph", СТАЛО "pH Sensor"
    PRESSURE = (4, "load Cell")  # ← БЫЛО "pressure", СТАЛО "load Cell"
    VIBRATION = (5, "vibration")

    def __new__(cls, value: int, label: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self) -> str:
        return self.label

@dataclass(frozen=True)
class Payload:
    category: SensorType
    data: Union[float, str]

    def to_dict(self) -> dict:
        return {"category": str(self.category), "data": self.data}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'))

@dataclass(frozen=True)
class MqttMessage:
    device_id: str
    payload: str

    @classmethod
    def from_payload(cls, device_id: str, payload: Payload) -> "MqttMessage":
        payload_json = payload.to_json()
        payload_b64 = base64.b64encode(payload_json.encode("utf-8")).decode("ascii")
        return cls(device_id=device_id, payload=f"{device_id}.{payload_b64}")

    def to_bytes(self) -> bytes:
        return self.payload.encode("utf-8")

    @staticmethod
    def generate_device_id() -> str:
        return str(uuid.uuid4())