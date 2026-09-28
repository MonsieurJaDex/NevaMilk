import asyncio
from amqtt.broker import Broker

# Настройки брокера: разрешаем подключения без пароля на порт 1883
config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '127.0.0.1:1883', # 127.0.0.1 означает "локальный компьютер"
        }
    },
    'sys_interval': 0,
}

async def start_broker():
    broker = Broker(config)
    print("Запуск локального MQTT-брокера...")
    await broker.start()
    print("Брокер успешно запущен и ждет подключений на порту 1883!")
    
    # Держим брокер запущенным вечно
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(start_broker())
    except KeyboardInterrupt:
        print("\nБрокер остановлен.")
