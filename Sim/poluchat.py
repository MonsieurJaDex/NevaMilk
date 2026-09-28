import time
from paho.mqtt import client as mqtt_client

# Настройки должны строго совпадать с издателем
broker = "localhost" 
port = 1883
topic = "test/topic"
client_id = "python-mqtt-subscriber" # УНИКАЛЬНОЕ ИМЯ (НЕ такое же, как у издателя)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Успешно подключились к брокеру!")
        # Подписываемся на топик при успешном коннекте
        client.subscribe(topic)
        print(f"Подписались на топик: {topic}")
    else:
        print(f"Ошибка подключения, код: {rc}")

def on_message(client, userdata, msg):
    # Эта функция сработает, когда прилетит сообщение
    print(f"Пришло сообщение: '{msg.payload.decode()}' из топика '{msg.topic}'")

def run():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port)
    
    print("Получатель запущен и ждет сообщения...")
    client.loop_forever() # Держим программу активной вечно

if __name__ == '__main__':
    run()
