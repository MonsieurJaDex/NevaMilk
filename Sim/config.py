import os

# 1. Берем URL из .env или ставим "mosquitto:1883" по умолчанию
broker_url = os.getenv("MQTT_BROKER_URL", "mosquitto:1883")

# 2. Делим СПРАВА НАЛЕВО ровно 1 раз по двоеточию.
# Это работает и для "mosquitto:1883", и для "mqtt://mosquitto:1883"
BROKER_HOST, BROKER_PORT_STR = broker_url.rsplit(":", 1)
BROKER_PORT = int(BROKER_PORT_STR)

# 3. Остальные настройки
CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "python-simulator-sensor")
TOPIC_TELEMETRY = os.getenv("MQTT_TOPIC_ANALYTICS", "sensors/analytics")
TOPIC_ALERTS = os.getenv("MQTT_TOPIC_WARNINGS", "sensors/warnings")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"