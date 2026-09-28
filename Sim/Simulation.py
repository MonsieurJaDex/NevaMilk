import random
from enum import Enum
from datetime import datetime

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

def get_cooking_data():
    """Генератор с реалистичным нагревом и искусственными случайными сбоями после стабилизации"""
    total_seconds = 0
    temperature = 20.0
    
    stages = [
        ProcessStage.SMOKE_1, 
        ProcessStage.SUSHKA_1, 
        ProcessStage.SMOKE_2, 
        ProcessStage.SUSHKA_2
    ]
    
    for stage in stages:
        is_stabilized = False 
        
        for stage_second in range(1, 21):
            total_seconds += 1
            
            direction = stage.target_temp - temperature
            temperature += (direction * 0.2)
            
            if not is_stabilized and (stage.min_norm <= temperature <= stage.max_norm):
                is_stabilized = True
            
            if is_stabilized:
                if random.random() < 0.15: #15% на случайное изменение
                    anomaly_jump = random.choice([random.uniform(6, 10), random.uniform(-10, -6)])
                    current_temp = round(temperature + anomaly_jump, 1)
                else:
                    current_temp = round(temperature + random.uniform(-0.5, 0.5), 1)
            else:
                current_temp = round(temperature + random.uniform(-0.5, 0.5), 1)
            
            if is_stabilized and (current_temp < stage.min_norm or current_temp > stage.max_norm):
                is_anomaly = True
            else:
                is_anomaly = False
            
            current_status = "РАЗОГРЕВ" if not is_stabilized else ("АВАРИЯ" if is_anomaly else "НОРМА")
            
            step_data = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "stage": stage.stage_name,
                "temperature": current_temp,
                "stage_time_sec": stage_second,
                "total_time_sec": total_seconds,
                "is_anomaly": is_anomaly,
                "min_norm": stage.min_norm,
                "max_norm": stage.max_norm,
                "status": current_status
            }
            
            yield step_data
