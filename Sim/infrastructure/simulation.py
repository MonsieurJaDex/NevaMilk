import time
import random
from abc import ABC, abstractmethod
from core.models import Sensor
from core.schema import SensorType

# ==============================================================================
# 1. БАЗОВЫЙ КЛАСС ГЕНЕРАТОРА
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
        """Обновляет значение датчика с учётом физики и погрешности"""
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
# 2. КОНКРЕТНЫЕ ГЕНЕРАТОРЫ (с реальными спецификациями)
# ==============================================================================

class PT100Generator(BaseSensorGenerator):
    """
    Температура: PT100 Class B (ГОСТ 6651-2011)
    - Диапазон: -200...+850°C
    - Погрешность: ±(0.3 + 0.005×|t|)°C → ~±0.5°C при 70-90°C
    - Время отклика: 0.5-2 сек
    """
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        target = stage_info["target_temp"]
        
        # Инерция нагрева/охлаждения (реальная тепловая инерция камеры)
        self.value += (target - self.value) * 0.12
        
        # Шум датчика PT100 Class B (±0.5°C)
        if random.random() < 0.03:  # 3% шанс сбоя
            self.value += random.uniform(-2.0, 2.0)  # Резкий скачок
        else:
            self.value += random.uniform(-0.25, 0.25)  # Нормальный шум ±0.5°C
            
        self.value = max(20.0, min(120.0, self.value))
        return self.value


class HumidityCapGenerator(BaseSensorGenerator):
    """
    Влажность: Ёмкостный датчик (типа SHT30)
    - Диапазон: 0-100% RH
    - Погрешность: ±2% RH
    - Обратная зависимость от температуры
    """
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        temp = other_sensors.get("Temperature", 70.0)
        stage = stage_info["name"]
        
        # Реальная физика: при нагреве влажность падает
        if "СУШКА" in stage:
            target_hum = 55.0 - (temp - 50.0) * 0.3  # 40-55%
        elif "КОПЧЕНИЕ" in stage:
            target_hum = 65.0 - (temp - 60.0) * 0.4  # 50-65%
        else:
            target_hum = 70.0 - (temp - 40.0) * 0.2  # 60-70%
        
        self.value += (target_hum - self.value) * 0.08  # Инерция
        self.value += random.uniform(-1.0, 1.0)  # Погрешность ±2%
        self.value = max(30.0, min(80.0, self.value))
        return self.value


class LoadCellGenerator(BaseSensorGenerator):
    """
    Давление/Вес: Тензодатчик (Load Cell)
    - Диапазон: 980-1050 hPa (атмосферное + давление в камере)
    - Погрешность: ±0.5 hPa
    - Зависит от температуры (тепловое расширение)
    """
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        temp = other_sensors.get("Temperature", 70.0)
        
        # Атмосферное давление + влияние температуры
        base_pressure = 1013.25
        temp_effect = (temp - 20.0) * 0.02  # +0.02 hPa на каждый °C
        
        target_press = base_pressure + temp_effect
        self.value += (target_press - self.value) * 0.05
        self.value += random.uniform(-0.25, 0.25)  # Погрешность ±0.5 hPa
        return self.value


class VibrationGenerator(BaseSensorGenerator):
    """
    Вибрация: Промышленный акселерометр
    - Диапазон: 0-50 mm/s
    - Погрешность: ±5%
    - Зависит от этапа (вентиляторы, дымососы)
    """
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        stage = stage_info["name"]
        
        # Реальная физика: оборудование работает на разных этапах
        if "КОПЧЕНИЕ" in stage:
            # Дымососы и вентиляторы работают
            target_vib = 2.5 + random.uniform(-0.3, 0.3)
            self.value += (target_vib - self.value) * 0.1
        elif "СУШКА" in stage:
            # Только вентиляция
            target_vib = 1.2 + random.uniform(-0.2, 0.2)
            self.value += (target_vib - self.value) * 0.08
        else:
            # Покой
            target_vib = 0.3
            self.value += (target_vib - self.value) * 0.05
            
        self.value += random.uniform(-0.1, 0.1)
        self.value = max(0.1, min(5.0, self.value))
        return self.value


class PHSensorGenerator(BaseSensorGenerator):
    """
    pH: Стеклянный электрод (для контроля среды)
    - Диапазон: 0-14 pH
    - Погрешность: ±0.05 pH
    - Очень стабильный, медленный дрейф
    """
    def update(self, stage_info: dict, other_sensors: dict) -> float:
        # Медленный дрейф + шум
        self.value += random.uniform(-0.02, 0.02)
        self.value = max(5.5, min(7.5, self.value))
        return self.value

# ==============================================================================
# 3. ФАБРИКА (Factory Method)
# ==============================================================================

class SensorFactory:
    @staticmethod
    def create_generator(sensor_type: SensorType, stage_info: dict) -> BaseSensorGenerator:
        """Фабричный метод: создаёт нужный генератор по типу датчика"""
        
        if sensor_type == SensorType.PT100:
            return PT100Generator(
                name="Temperature", sensor_type=sensor_type, unit="°C",
                min_norm=stage_info["min_temp"], max_norm=stage_info["max_temp"],
                initial_value=22.0
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
# 4. ОРКЕСТРАТОР СИМУЛЯЦИИ (с реальными параметрами ГОСТ)
# ==============================================================================

def generate_sensors():
    """
    Главный генератор на основе реальных параметров коптильной камеры.
    Источник: Таблица параметров программ коптильной камеры (ГОСТ)
    """
    
    # Реальные этапы из таблицы (температура, время, допуски)
    stages = [
        {
            "name": "СУШКА 1",
            "target_temp": 70.0,
            "min_temp": 65.0,    # -5°C допуск
            "max_temp": 75.0,    # +5°C допуск
            "duration": 12,      # минут
        },
        {
            "name": "КОПЧЕНИЕ 1",
            "target_temp": 90.0,
            "min_temp": 85.0,
            "max_temp": 95.0,
            "duration": 59,
        },
        {
            "name": "СУШКА 2",
            "target_temp": 70.0,
            "min_temp": 65.0,
            "max_temp": 75.0,
            "duration": 15,
        },
        {
            "name": "КОПЧЕНИЕ 2",
            "target_temp": 90.0,
            "min_temp": 85.0,
            "max_temp": 95.0,
            "duration": 90,
        },
        {
            "name": "ОХЛАЖДЕНИЕ",
            "target_temp": 45.0,
            "min_temp": 40.0,
            "max_temp": 50.0,
            "duration": 110,
        },
    ]
    
    for stage in stages:
        print(f"\n🔄 Этап: {stage['name']} | Цель: {stage['target_temp']}°C | Время: {stage['duration']} мин")
        
        # Фабрика создаёт генераторы для текущего этапа
        generators = [
            SensorFactory.create_generator(SensorType.PT100, stage),
            SensorFactory.create_generator(SensorType.HUMIDITY_CAP, stage),
            SensorFactory.create_generator(SensorType.PH, stage),
            SensorFactory.create_generator(SensorType.LOAD_CELL, stage),
            SensorFactory.create_generator(SensorType.VIBRATION, stage),
        ]
        
        # Цикл симуляции времени (1 итерация = 1 минута реального времени)
        for minute in range(stage["duration"]):
            current_readings = {}
            sensors_to_yield = []
            
            for gen in generators:
                # Обновляем значение с учётом физики
                gen.update(stage, current_readings)
                
                sensor = gen.get_sensor()
                sensors_to_yield.append(sensor)
                current_readings[gen.name] = sensor.value
            
            yield sensors_to_yield
            time.sleep(1)  # 1 секунда = 1 минута процесса (ускорено для демонстрации)
