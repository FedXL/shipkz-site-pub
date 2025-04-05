import os
import subprocess
import time
from celery import shared_task
from django.conf import settings

from app_bot.management.bot_core import sync_bot
from legacy.models import Orders

GIF = 'CgACAgIAAxkBAAEENRlnQJgNXcixMTqz_cQXMpMXjMFlQAACKGEAAvm7CUqwCiPSP3ms6jYE'

@shared_task()
def send_bf_gif():
    text = (
        "<b>Черная пятница на Tradeinn</b>\n\n"
        "Распродажи стартовали, лучше не откладывать. "
        "Интересные позиции обычно быстро заканчиваются.\n\n"
        "<b>Промокод BF15 -15%</b>"
    )
    gif = GIF
    orders = Orders.objects.filter(client__isnull=False)
    clients_id = [order.client.user_id for order in orders]
    clean_clients_id = set(clients_id)
    for num ,client_id in enumerate(clean_clients_id):
        result = sync_bot.send_gif(client_id, gif, caption=text)
        time.sleep(0.2)
    return 'Success send telegram message with photo'


@shared_task()
def create_dump():
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")  # По умолчанию 5432

    # Папка, куда сохранять дамп
    DUMP_DIR = "/app/dumps"
    DUMP_FILE = os.path.join(DUMP_DIR, f"ship_kz.dump")
    os.makedirs(DUMP_DIR, exist_ok=True)

    dump_command = (
        f'PGPASSWORD="{DB_PASSWORD}" pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} '
        f'-d {DB_NAME} -F c -f {DUMP_FILE}'
    )
    try:
        subprocess.run(dump_command, shell=True, check=True, text=True)
        print(f"✅ Дамп базы данных {DB_NAME} сохранён в {DUMP_FILE}")
        time.sleep(2)
        sync_bot.send_dump(chat_id=settings.ORDERS_CATCH_CHAT, file_path=DUMP_FILE)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании дампа: {e}")







