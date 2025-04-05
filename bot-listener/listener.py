import asyncio
import json
import logging
import os
import django
from channels.layers import get_channel_layer
from django.conf import settings
from redis.asyncio import Redis
from redis.exceptions import RedisError
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shipkz.settings")
django.setup()
console_logger = logging.getLogger("console_logger")
console_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
console_logger.addHandler(console_handler)


REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_CHANNEL = "menu"


async def handle_message(message):
    """
    Обработка сообщений из Redis.
    """
    console_logger.warning('start handle_message V1.0 easy send messsage')
    try:
        console_logger.info(f"Получено сообщение!: {message}")
        if message["type"] != "message":
            return
        data = json.loads(message["data"])
        console_logger.info(f"Данные сообщения: {data}")
        web_user_id = data.get("web_user_id", None)
        consumer_foo = data.get("consumer_foo", None)
        if not web_user_id:
            console_logger.error("Ошибка: userID не найден в сообщении.")
            return
        if not consumer_foo:
            console_logger.error("Ошибка: foo_name не найден в сообщении.")
            return

        console_logger.info(f"Получение канала для userID: {web_user_id}")
        redis_client = settings.REDIS_CONNECTION
        channel_name = redis_client.get(f"ws_user_id_{web_user_id}")

        if not channel_name:
            console_logger.error(f"Ошибка: канал для userID {web_user_id} не найден.")
            return

        console_logger.info(f"Канал для userID {web_user_id}: {channel_name}")
        channel_name = channel_name.decode("utf-8")
        channel_layer = get_channel_layer()

        await channel_layer.send(
            channel_name,
            {
                "type": consumer_foo,
                "message_data": data,
            }
        )
    except Exception as e:
        console_logger.error(f"Ошибка обработки сообщения: {e}")


async def start_redis_listener():
    """
    Асинхронный подписчик на канал Redis.
    """
    redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT)
    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(REDIS_CHANNEL)
        console_logger.info(f"Подписан на канал: {REDIS_CHANNEL}")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await handle_message(message)
            await asyncio.sleep(0.01)
    except RedisError as e:
        console_logger.error(f"Ошибка Redis: {e}")
    finally:
        console_logger.warning("Закрытие соединения с Redis.")
        await redis_client.close()

if __name__ == "__main__":
    asyncio.run(start_redis_listener())


