import os
import uuid
import paho.mqtt.client as mqtt
from config import BROKER_HOST, BROKER_PORT, CLIENT_ID

class MQTTClientWrapper:
    def __init__(self):
        # UUID станка из .env или генерируем новый
        self.device_id = os.getenv("MACHINE_UUID", str(uuid.uuid4()))
        
        self.client = mqtt.Client(client_id=f"{CLIENT_ID}-{self.device_id[:8]}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ MQTT подключён | Станок: {self.device_id}")
        else:
            print(f"❌ MQTT ошибка подключения: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        print("⚠️  MQTT отключён")

    def start(self):
        self.client.connect(BROKER_HOST, BROKER_PORT, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()