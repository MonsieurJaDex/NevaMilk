# infrastructure/simulation.py
import random
from core.models import ProcessStage

def get_cooking_data():
    """Генератор данных с флагом стабилизации."""
    temperature = 20.0
    
    stages = [
        ProcessStage.SMOKE_1, 
        ProcessStage.SUSHKA_1, 
        ProcessStage.SMOKE_2, 
        ProcessStage.SUSHKA_2
    ]
    
    for stage in stages:
        is_stabilized = False 
        
        for _ in range(1, 21):
            # Физика нагрева
            direction = stage.target_temp - temperature
            temperature += (direction * 0.2)
            
            # Проверка выхода на режим
            if not is_stabilized and (stage.min_norm <= temperature <= stage.max_norm):
                is_stabilized = True
            
            # Эмуляция шума и сбоев
            if is_stabilized:
                if random.random() < 0.15: #15%
                    anomaly_jump = random.choice([random.uniform(6, 10), random.uniform(-10, -6)])
                    current_temp = round(temperature + anomaly_jump, 1)
                else:
                    current_temp = round(temperature + random.uniform(-0.5, 0.5), 1)
            else:
                current_temp = round(temperature + random.uniform(-0.5, 0.5), 1)
            
            yield {
                "temperature": current_temp,
                "min_norm": stage.min_norm,
                "max_norm": stage.max_norm,
                "is_stabilized": is_stabilized
            }