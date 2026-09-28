import time
from paho.mqtt import client as mqtt_client
from enum import Enum, auto
from datetime import datetime
import json
from Simulation import get_cooking_data

broker = "localhost" 
port = 1883
topic = "test/topic"
client_id = "python-mqtt-publisher"

TOPIC_TELEMETRY = "test/topic"
TOPIC_ALERTS = "test/alerts"

def connect_mqtt():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id)
    client.connect(broker, port)
    return client

def publish_process(client):
    data_stream = get_cooking_data()
    
    for data in data_stream:
        time.sleep(1)
        if data["is_anomaly"]:
            alert_payload = {
                "timestamp": data["timestamp"],
                "stage": data["stage"],
                "temperature": data["temperature"],
                "message": f"Выход за рамки нормы ({data['min_norm']} - {data['max_norm']}°C)"
            }
            client.publish(TOPIC_ALERTS, json.dumps(alert_payload, ensure_ascii=False))
            print(f"[ОТПРАВЛЕН ALERT] -> {data['temperature']}°C")

        telemetry_payload = {
            "timestamp": data["timestamp"],
            "stage": data["stage"],
            "temperature": data["temperature"],
            "stage_time_sec": data["stage_time_sec"],
            "total_time_sec": data["total_time_sec"]
        }
        
        result = client.publish(TOPIC_TELEMETRY, json.dumps(telemetry_payload, ensure_ascii=False))
        if result.rc == 0:
            print(f"[ОТПРАВЛЕНА ТЕЛЕМЕТРИЯ] -> {data['stage']} ({data['temperature']}°C)")
        else:
            print(f"Ошибка сети MQTT. Код: {result.rc}")

def run():
    client = connect_mqtt()
    client.loop_start()
    time.sleep(1)
    
    try:
        publish_process(client)
    except KeyboardInterrupt:
        print("\n Отправка остановлена.")
    finally:
        client.loop_stop()

if __name__ == '__main__':
    run()