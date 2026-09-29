# ~/NevaMilk/Sim/services/telemetry_sender.py
import time
from core.models import TelemetryPoint
from infrastructure.mqtt_client import MQTTClientWrapper
from infrastructure.simulation import get_cooking_data
from config import TOPIC_TELEMETRY, TOPIC_ALERTS, DEBUG

class TelemetrySender:
    def __init__(self, mqtt_client: MQTTClientWrapper):
        self.mqtt = mqtt_client

    def run(self):
        print("🚀 Запуск симуляции датчиков...")
        print(f"📡 Телеметрия -> {TOPIC_TELEMETRY}")
        print(f"⚠️  Warning -> {TOPIC_ALERTS}")
        print("-" * 50)
        
        cycle_count = 0
        
        # ─── БЕСКОНЕЧНЫЙ ЦИКЛ ───
        while True:
            cycle_count += 1
            print(f"\n🔄 Цикл симуляции #{cycle_count}")
            
            raw_data_stream = get_cooking_data()
            
            for raw_data in raw_data_stream:
                point = TelemetryPoint(**raw_data)
                
                # 1. Отправляем телеметрию (всегда)
                self.mqtt.publish_message(TOPIC_TELEMETRY, point.to_telemetry_payload())
                
                # 2. Отправляем WARNING (только если авария после стабилизации)
                if point.is_anomaly:
                    self.mqtt.publish_message(TOPIC_ALERTS, point.to_warning_payload())
                    
                    if point.temperature > point.max_norm:
                        print(f"[️  WARNING] {point.temperature}°C (TOO HIGH)")
                    else:
                        print(f"[⚠️  WARNING] {point.temperature}°C (TOO LOW)")
                else:
                    status = " РАЗОГРЕВ" if not point.is_stabilized else "✅ ОК"
                    print(f"[{status}] {point.temperature}°C")
                
                time.sleep(1)
            
            # Пауза между циклами (5 секунд), чтобы не спамить
            print("⏳ Пауза 5 секунд перед новым циклом...")
            time.sleep(5)