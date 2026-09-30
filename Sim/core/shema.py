from __future__ import annotations
import base64
import json
import uuid
from dataclasses import dataclass
from enum import IntEnum
from typing import Union

# ─── UUID ДЛЯ КАЖДОГО ТИПА ДАТЧИКА (постоянные!) ───
SENSOR_UUIDS = {
    "pt100 Needle":        "d669aa34-3c3b-4760-a9db-ee95d2285ecd",
    "pt1000 RTD":          "3542693e-0e36-40ff-a3f5-6542f3c77750",
    "pH Sensor":           "c33545a1-6e44-453b-bfb5-7ef84a71c43f",
    "humidity":            "f7711802-75ba-4915-b592-c7df6c9f30db",
    "psychrometric":       "3d0255fd-555e-433b-a7b4-fdfb9a0684cd",
    "load Cell":           "8f96521b-4044-4735-a3ea-a337e69cfacc",
    "capacitive Level":    "f1c9e5f1-17da-48e5-bdad-e63138dd4be3",
    "computer Vision":     "50377713-8dbf-4049-8de5-4b856ae9e497",
    "temperature":         "32fc5ea5-0483-4e51-8664-15e790296a62",
    "vibration":           "1a1aba96-fabe-42e4-8778-b9238debc721",
}

class SensorType(IntEnum):
    """Типы датчиков — СТРОГО как в map[SensorType]string в Go"""
    UNKNOWN = (0, "unknown")
    PT100 = (1, "pt100 Needle")
    PT1000 = (2, "pt1000 RTD")
    PH = (3, "pH Sensor")
    HUMIDITY_CAP = (4, "humidity")
    PSYCHROMETRIC = (5, "psychrometric")
    LOAD_CELL = (6, "load Cell")
    LEVEL_CAP = (7, "capacitive Level")
    COMPUTER_VISION = (8, "computer Vision")
    TEMPERATURE = (9, "temperature")
    VIBRATION = (10, "vibration")

    def __new__(cls, value: int, label: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self) -> str:
        return self.label

    def get_uuid(self) -> str:
        return SENSOR_UUIDS.get(self.label, str(uuid.uuid4()))

@dataclass(frozen=True)
class TelemetryPayload:
    """JSON: uuid, name, category, data"""
    uuid: str
    name: str
    category: str
    data: Union[float, str]

    def to_json(self) -> str:
        return json.dumps({
            "uuid": self.uuid,
            "name": self.name,
            "category": self.category,
            "data": self.data
        }, separators=(',', ':'))

@dataclass(frozen=True)
class MqttMessage:
    payload_json: str

    @classmethod
    def create(cls, payload: TelemetryPayload) -> "MqttMessage":
        return cls(payload_json=payload.to_json())

    def to_bytes(self) -> bytes:
        return self.payload_json.encode("utf-8")
