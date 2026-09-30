import time
import base64
from core.models import Sensor
from core.schema import TelemetryPayload
from infrastructure.mqtt_client import MQTTClientWrapper
from infrastructure.simulation import generate_sensors
from config import TOPIC_TELEMETRY, TOPIC_ALERTS

class TelemetrySender:
    def __init__(self, mqtt_client: MQTTClientWrapper):
        self.mqtt = mqtt_client

    def _encode_message(self, payload: TelemetryPayload) -> str:
        """Кодирует payload в формат: uuid.base64(json)"""
        json_str = payload.to_json()
        b64_str = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
        return f"{payload.uuid}.{b64_str}"

    def run(self):
        print("🚀 Запуск симуляции датчиков...")
        print(f"📡 Телеметрия -> {TOPIC_TELEMETRY}")
        print(f"⚠️  Warning -> {TOPIC_ALERTS}")
        print(f"🆔 Станок ID: {self.mqtt.device_id}")
        print("-" * 50)
        
        sensor_generator = generate_sensors()
        
        while True:
            sensors = next(sensor_generator)
            
            for sensor in sensors:
                # Отправляем телеметрию
                msg = self._encode_message(sensor.to_telemetry())
                
                # 🔍 ОТАДКА: печатаем ЧТО ИМЕННО уходит в MQTT
                print(f"📤 [{sensor.name:12}] -> {msg}")
                
                self.mqtt.client.publish(TOPIC_TELEMETRY, msg)
                
                # Проверяем аномалию
                if sensor.is_anomaly:
                    warn_msg = self._encode_message(sensor.to_warning())
                    self.mqtt.client.publish(TOPIC_ALERTS, warn_msg)
                    print(f"[⚠️  {sensor.name:12}] {sensor.value:6} {sensor.unit:4}")
                else:
                    print(f"[✅  {sensor.name:12}] {sensor.value:6} {sensor.unit:4}")
            
            time.sleep(1)
