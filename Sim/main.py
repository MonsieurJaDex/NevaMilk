# main.py
from infrastructure.mqtt_client import MQTTClientWrapper
from service.telemetry_sender import TelemetrySender

def main():
    mqtt = None
    try:
        mqtt = MQTTClientWrapper()
        print(f"Device ID: {mqtt.device_id}")
        mqtt.start()
        
        sender = TelemetrySender(mqtt)
        sender.run()
        
    except KeyboardInterrupt:
        print("\nОстановка пользователем.")
    except ConnectionRefusedError:
        print("Ошибка: Не удалось подключиться к MQTT брокеру!")
    finally:
        if mqtt is not None:
            mqtt.stop()
            print("Соединение закрыто.")

if __name__ == '__main__':
    main()