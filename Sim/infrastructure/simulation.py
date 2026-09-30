import time
import random
from abc import ABC, abstractmethod
from core.models import Sensor
from core.schema import SensorType

# ==============================================================================
# 1. БАЗОВЫЙ КЛАСС ГЕНЕРАТОРА (Product Interface)
# ==============================================================================
class BaseSensorGenerator(ABC):
    def __init__(self, name: str, sensor_type: SensorType, unit: str, 
                 min_norm: float, max_norm: float, initial_value: float):
        self.name = name
        self.sensor_type = sensor_type
        self.unit = unit
        self.min_norm = min_norm
        self.max_norm = max_norm
        self.value = initial_value

    @abstractmethod
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        """Обновляет значение датчика с учетом физики и погрешности"""
        pass

    def get_sensor(self) -> Sensor:
        """Возвращает объект Sensor для отправки"""
        return Sensor(
            name=self.name,
            sensor_type=self.sensor_type,
            value=float(round(self.value, 2)),
            unit=self.unit,
            min_norm=self.min_norm,
            max_norm=self.max_norm
        )

# ==============================================================================
# 2. КОНКРЕТНЫЕ ГЕНЕРАТОРЫ (Concrete Products)
# ==============================================================================

class PT100Generator(BaseSensorGenerator):
    """Температура: PT100 Class B (погрешность ±0.3°C), инерция нагрева"""
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        target = stage_info["target"]
        # Инерция нагрева/охлаждения
        self.value += (target - self.value) * 0.15
        
        # Шум датчика и редкие аномалии
        if random.random() < 0.05:  # 5% шанс сбоя
            self.value += random.uniform(-2.0, 2.0)
        else:
            self.value += random.uniform(-0.15, 0.15)  # Реальная погрешность ±0.3°C
            
        self.value = max(20.0, min(95.0, self.value))
        return self.value


class HumidityCapGenerator(BaseSensorGenerator):
    """Влажность: Ёмкостный датчик (погрешность ±2% RH), обратно температуре"""
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        temp = other_sensors.get("Temperature", 25.0)
        target_hum = 70.0 - (temp - 20.0) * 0.4  # Чем горячее, тем суше
        
        self.value += (target_hum - self.value) * 0.1  # Инерция
        self.value += random.uniform(-1.0, 1.0)        # Погрешность ±2%
        self.value = max(30.0, min(80.0, self.value))
        return self.value


class LoadCellGenerator(BaseSensorGenerator):
    """Давление: Тензодатчик (погрешность ±0.5 hPa), медленный дрейф"""
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        temp = other_sensors.get("Temperature", 25.0)
        target_press = 1013.25 + (temp - 20.0) * 0.03
        
        self.value += (target_press - self.value) * 0.05
        self.value += random.uniform(-0.25, 0.25)      # Погрешность ±0.5 hPa
        return self.value


class VibrationGenerator(BaseSensorGenerator):
    """Вибрация: Акселерометр (погрешность ±5%), зависит от этапа"""
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        if "SMOKE" in stage_info["name"]:
            target_vib = 2.0 + random.uniform(-0.5, 0.5)  # Работа механизмов
            self.value += (target_vib - self.value) * 0.1
        else:
            target_vib = 0.3                              # Покой
            self.value += (target_vib - self.value) * 0.05
            
        self.value += random.uniform(-0.1, 0.1)
        self.value = max(0.1, min(5.0, self.value))
        return self.value


class PHSensorGenerator(BaseSensorGenerator):
    """pH: Стеклянный электрод (погрешность ±0.05 pH), очень стабильный"""
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        self.value += random.uniform(-0.02, 0.02)  # Медленный дрейф
        self.value = max(5.5, min(7.5, self.value))
        return self.value

# ==============================================================================
# 3. ФАБРИКА (Creator)
# ==============================================================================

class SensorFactory:
    @staticmethod
    def create_generator(sensor_type: SensorType, stage_info: dict) -> BaseSensorGenerator:
        """Фабричный метод: создает нужный генератор по типу датчика"""
        
        if sensor_type == SensorType.PT100:
            return PT100Generator(
                name="Temperature", sensor_type=sensor_type, unit="°C",
                min_norm=stage_info["min"], max_norm=stage_info["max"], initial_value=22.0
            )
        elif sensor_type == SensorType.HUMIDITY_CAP:
            return HumidityCapGenerator(
                name="Humidity", sensor_type=sensor_type, unit="%",
                min_norm=35.0, max_norm=75.0, initial_value=65.0
            )
        elif sensor_type == SensorType.LOAD_CELL:
            return LoadCellGenerator(
                name="Pressure", sensor_type=sensor_type, unit="hPa",
                min_norm=1002.0, max_norm=1018.0, initial_value=1013.25
            )
        elif sensor_type == SensorType.VIBRATION:
            return VibrationGenerator(
                name="Vibration", sensor_type=sensor_type, unit="mm/s",
                min_norm=0.0, max_norm=4.5, initial_value=0.3
            )
        elif sensor_type == SensorType.PH:
            return PHSensorGenerator(
                name="pH", sensor_type=sensor_type, unit="pH",
                min_norm=5.5, max_norm=7.5, initial_value=6.8
            )
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

# ==============================================================================
# 4. ОРКЕСТРАТОР СИМУЛЯЦИИ
# ==============================================================================

def generate_sensors():
    """Главный генератор, использующий Factory Method"""
    
    stages = [
        {"name": "SMOKE_1", "target": 75.0, "min": 70.0, "max": 80.0, "duration": 25},
        {"name": "SUSHKA_1", "target": 55.0, "min": 50.0, "max": 60.0, "duration": 20},
        {"name": "SMOKE_2", "target": 85.0, "min": 80.0, "max": 90.0, "duration": 25},
        {"name": "SUSHKA_2", "target": 40.0, "min": 35.0, "max": 45.0, "duration": 20},
    ]
    
    for stage in stages:
        # 1. Фабрика создает набор генераторов для текущего этапа
        generators = [
            SensorFactory.create_generator(SensorType.PT100, stage),
            SensorFactory.create_generator(SensorType.HUMIDITY_CAP, stage),
            SensorFactory.create_generator(SensorType.PH, stage),
            SensorFactory.create_generator(SensorType.LOAD_CELL, stage),
            SensorFactory.create_generator(SensorType.VIBRATION, stage),
        ]
        
        # 2. Цикл симуляции времени
        for _ in range(stage["duration"]):
            current_readings = {}
            sensors_to_yield = []
            
            for gen in generators:
                # Обновляем значение, передавая показания других датчиков для корреляции
                gen.update(stage, current_readings)
                
                sensor = gen.get_sensor()
                sensors_to_yield.append(sensor)
                current_readings[gen.name] = sensor.value
            
            yield sensors_to_yield
            time.sleep(1)
