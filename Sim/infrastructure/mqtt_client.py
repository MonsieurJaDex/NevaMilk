# infrastructure/mqtt_client.py
import paho.mqtt.client as mqtt
from config import BROKER_HOST, BROKER_PORT, CLIENT_ID
from core.shema import MqttMessage, Payload

class MQTTClientWrapper:
    def __init__(self):
        # Генерируем уникальный UUID для этого устройства
        self.device_id = MqttMessage.generate_device_id()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
        self.client.connect(BROKER_HOST, BROKER_PORT)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def publish_message(self, topic: str, payload: Payload):
        """Отправляет сообщение в формате uuid.base64(json)"""
        msg = MqttMessage.from_payload(self.device_id, payload)
        result = self.client.publish(topic, msg.to_bytes())
        return result.rc == 0