# poluchat.py
import time
import json
import base64
from paho.mqtt import client as mqtt_client
from core.shema import SensorType

# --- НАСТРОЙКИ ---
BROKER = "localhost"
PORT = 1883
CLIENT_ID = "python-mqtt-subscriber"  # Уникальное имя (не как у издателя)

TOPIC_TELEMETRY = "test/topic"        # Для графиков
TOPIC_ALERTS = "test/al_topic"        # Для предупреждений

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Успешно подключились к брокеру!")
        client.subscribe(TOPIC_TELEMETRY)
        client.subscribe(TOPIC_ALERTS)
        print(f"📡 Подписка: {TOPIC_TELEMETRY}")
        print(f"⚠️  Подписка: {TOPIC_ALERTS}")
        print("-" * 70)
    else:
        print(f" Ошибка подключения, код: {rc}")

def decode_message(raw_payload: bytes):
    """Декодирует формат: uuid.base64(json)"""
    try:
        raw_str = raw_payload.decode("utf-8")
        parts = raw_str.split(".", 1)
        if len(parts) != 2:
            return None, None, raw_str
        
        device_id = parts[0]
        payload_json = base64.b64decode(parts[1]).decode("utf-8")
        payload_data = json.loads(payload_json)
        
        return device_id, payload_data, raw_str
    except Exception as e:
        return None, f"Ошибка декодирования: {e}", raw_payload.decode("utf-8", errors="replace")

def on_message(client, userdata, msg):
    device_id, data, raw_base64 = decode_message(msg.payload)
    
    # ─── ОТОБРАЖЕНИЕ СЫРОГО BASE64 ───
    print(f"\n[RAW BASE64] {raw_base64}")
    
    if data is None or isinstance(data, str):
        print(f" {msg.topic}: {data}")
        return

    # ─── ТЕЛЕМЕТРИЯ (для графиков) ───
    if msg.topic == TOPIC_TELEMETRY:
        temperature = data.get("data", {}).get("temperature", "N/A")
        print(f"📡 [ГРАФИК] Device: {device_id} | Temp: {temperature}°C")
        print(f"   📄 Decoded: {json.dumps(data, ensure_ascii=False)}")
    
    # ─── ALERT / WARNING ───
    elif msg.topic == TOPIC_ALERTS:
        warning_msg = data.get("data", "N/A")  # Строка: "temperature is too high/low"
        category = data.get("category", "unknown")
        print(f"⚠️  [ALERT] Device: {device_id} | {category}: {warning_msg}")
        print(f"    Decoded: {json.dumps(data, ensure_ascii=False)}")

def run():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)
    
    print("🚀 Получатель запущен и ждет сообщения...")
    print(f"   Брокер: {BROKER}:{PORT}")
    client.loop_forever()

if __name__ == '__main__':
    run()