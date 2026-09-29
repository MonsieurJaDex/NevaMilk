# service/telemetry_sender.py
import time
from core.models import SensorPoint
from core.schema import SensorType, MqttMessage
from infrastructure.mqtt_client import MQTTClientWrapper
from infrastructure.simulation import get_cooking_data
from config import TOPIC_TELEMETRY, TOPIC_ALERTS

class TelemetrySender:
    def __init__(self, mqtt_client: MQTTClientWrapper):
        self.mqtt = mqtt_client

    def run(self):
        print("🚀 Запуск симуляции датчиков...")
        print(f"📡 Телеметрия -> {TOPIC_TELEMETRY}")
        print(f"⚠️  Warning -> {TOPIC_ALERTS}")
        print(f"🆔 Device ID: {self.mqtt.device_id}")
        print("-" * 50)
        
        cycle_count = 0
        
        while True:
            cycle_count += 1
            print(f"\n🔄 Цикл #{cycle_count}")
            
            # ─── ГЕНЕРИРУЕМ ОДИН UUID НА ВЕСЬ ЦИКЛ ───
            cycle_uuid = self.mqtt.device_id
            print(f"📦 UUID цикла: {cycle_uuid}")
            
            for raw_data in get_cooking_data():
                # ─── 1. ТЕМПЕРАТУРА ───
                temp_point = SensorPoint(
                    sensor_type=SensorType.TEMPERATURE,
                    value=float(raw_data["temperature"]),
                    unit="°C",
                    min_norm=float(raw_data["min_norm"]),
                    max_norm=float(raw_data["max_norm"]),
                    is_stabilized=raw_data["is_stabilized"]
                )
                self._send_message(TOPIC_TELEMETRY, temp_point.to_telemetry_payload(), cycle_uuid)
                
                if temp_point.is_anomaly:
                    self._send_message(TOPIC_ALERTS, temp_point.to_warning_payload(), cycle_uuid)
                    print(f"[⚠️  WARNING] Температура: {temp_point.value}°C")
                else:
                    status = " РАЗОГРЕВ" if not temp_point.is_stabilized else "✅ ОК"
                    print(f"[{status}] Температура: {temp_point.value}°C")
                
                # ─── 2. ВЛАЖНОСТЬ ───
                humidity_point = SensorPoint(
                    sensor_type=SensorType.HUMIDITY,
                    value=float(raw_data["humidity"]),
                    unit="%",
                    min_norm=35.0,
                    max_norm=75.0,
                    is_stabilized=True
                )
                self._send_message(TOPIC_TELEMETRY, humidity_point.to_telemetry_payload(), cycle_uuid)
                
                if humidity_point.is_anomaly:
                    self._send_message(TOPIC_ALERTS, humidity_point.to_warning_payload(), cycle_uuid)
                    print(f"[⚠️  WARNING] Влажность: {humidity_point.value}%")
                
                # ─── 3. pH ───
                ph_point = SensorPoint(
                    sensor_type=SensorType.PH,
                    value=float(raw_data["ph"]),
                    unit="pH",
                    min_norm=5.5,
                    max_norm=7.5,
                    is_stabilized=True
                )
                self._send_message(TOPIC_TELEMETRY, ph_point.to_telemetry_payload(), cycle_uuid)
                
                if ph_point.is_anomaly:
                    self._send_message(TOPIC_ALERTS, ph_point.to_warning_payload(), cycle_uuid)
                    print(f"[⚠️  WARNING] pH: {ph_point.value}")
                
                # ─── 4. ДАВЛЕНИЕ ───
                pressure_point = SensorPoint(
                    sensor_type=SensorType.PRESSURE,
                    value=float(raw_data["pressure"]),
                    unit="hPa",
                    min_norm=1002.0,
                    max_norm=1018.0,
                    is_stabilized=True
                )
                self._send_message(TOPIC_TELEMETRY, pressure_point.to_telemetry_payload(), cycle_uuid)
                
                if pressure_point.is_anomaly:
                    self._send_message(TOPIC_ALERTS, pressure_point.to_warning_payload(), cycle_uuid)
                    print(f"[⚠️  WARNING] Давление: {pressure_point.value} hPa")
                
                # ─── 5. ВИБРАЦИЯ ───
                vibration_point = SensorPoint(
                    sensor_type=SensorType.VIBRATION,
                    value=float(raw_data["vibration"]),
                    unit="mm/s",
                    min_norm=0.0,
                    max_norm=4.5,
                    is_stabilized=True
                )
                self._send_message(TOPIC_TELEMETRY, vibration_point.to_telemetry_payload(), cycle_uuid)
                
                if vibration_point.is_anomaly:
                    self._send_message(TOPIC_ALERTS, vibration_point.to_warning_payload(), cycle_uuid)
                    print(f"[⚠️  WARNING] Вибрация: {vibration_point.value} mm/s")
                
                time.sleep(1)
            
            print("⏳ Пауза 5 секунд...")
            time.sleep(5)
    
    def _send_message(self, topic: str, payload, device_id: str):
        """Отправляет сообщение с указанным UUID"""
        from core.schema import Payload
        msg = MqttMessage.from_payload(device_id, payload)
        self.mqtt.client.publish(topic, msg.to_bytes())