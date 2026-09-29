# infrastructure/simulation.py
import time
import random
from core.models import ProcessStage

def get_cooking_data():
    temperature = 20.0
    humidity = 60.0
    pressure = 1013.0
    vibration = 0.5
    
    stages = [
        ProcessStage.SMOKE_1, 
        ProcessStage.SUSHKA_1, 
        ProcessStage.SMOKE_2, 
        ProcessStage.SUSHKA_2
    ]
    
    for stage in stages:
        is_stabilized = False 
        
        for _ in range(20):
            # ТЕМПЕРАТУРА
            direction = stage.target_temp - temperature
            temperature += (direction * 0.2)
            
            if not is_stabilized and (stage.min_norm <= temperature <= stage.max_norm):
                is_stabilized = True
            
            if is_stabilized:
                if random.random() < 0.15:
                    temperature += random.uniform(-5, 5)
                else:
                    temperature += random.uniform(-0.5, 0.5)
            else:
                temperature += random.uniform(-0.5, 0.5)
            
            # ВЛАЖНОСТЬ
            target_humidity = 70.0 - (temperature - 20.0) * 0.5
            humidity += (target_humidity - humidity) * 0.1
            humidity += random.uniform(-2, 2)
            humidity = max(30.0, min(80.0, humidity))
            
            # ДАВЛЕНИЕ
            target_pressure = 1013.0 + (temperature - 20.0) * 0.05
            pressure += (target_pressure - pressure) * 0.1
            pressure += random.uniform(-0.5, 0.5)
            
            # ВИБРАЦИЯ
            if "SMOKE" in stage.stage_name:
                target_vibration = 2.5
                vibration += (target_vibration - vibration) * 0.2
                vibration += random.uniform(-0.3, 0.3)
            else:
                target_vibration = 0.5
                vibration += (target_vibration - vibration) * 0.1
            
            # pH
            current_ph = 6.5 + random.uniform(-0.5, 0.5)
            
            # Явное приведение ВСЕХ значений к float
            yield {
                "temperature": float(round(temperature, 1)),
                "min_norm": float(stage.min_norm),
                "max_norm": float(stage.max_norm),
                "is_stabilized": is_stabilized,
                "humidity": float(round(humidity, 1)),
                "humidity_anomaly": humidity > 75.0 or humidity < 35.0,
                "pressure": float(round(pressure, 1)),
                "pressure_anomaly": pressure > 1018.0 or pressure < 1002.0,
                "vibration": float(round(vibration, 2)),
                "vibration_anomaly": vibration > 4.5,
                "ph": float(round(current_ph, 2)),
                "ph_anomaly": current_ph > 7.5 or current_ph < 5.5,
            }
            
            time.sleep(1)