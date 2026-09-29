# ~/NevaMilk/Sim/config.py
import os

# 1. Получаем URL брокера из окружения
broker_url = os.getenv("MQTT_BROKER_URL", "localhost:1883")

# 2. Если есть префикс (mqtt:// или tcp://), отрезаем его
if "://" in broker_url:
    broker_url = broker_url.split("://", 1)[1]

# 3. Разделяем на хост и порт
if ":" in broker_url:
    BROKER_HOST, port_str = broker_url.split(":", 1)
    BROKER_PORT = int(port_str)
else:
    BROKER_HOST = broker_url
    BROKER_PORT = 1883

# 4. Остальные настройки
CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "python-simulator-sensor")
TOPIC_TELEMETRY = os.getenv("MQTT_TOPIC_ANALYTICS", "sensors/analytics")
TOPIC_ALERTS = os.getenv("MQTT_TOPIC_WARNINGS", "sensors/warnings")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"