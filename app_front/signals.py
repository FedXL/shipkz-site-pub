from celery.signals import task_failure
from django.conf import settings
from app_bot.management.bot_core import TelegramBot, sync_bot


@task_failure.connect
def handle_task_failure(sender, task_id, args, kwargs, einfo, **extras):
    """
    Обрабатывает все необработанные ошибки из задач Celery.
    """
    text = (f"Необработанная ошибка в задаче {sender.name} (ID: {task_id}): "
            f"Args: {args}, Kwargs: {kwargs}. Error: {einfo}")
    sync_bot.send_message(chat_id=settings.ORDERS_CATCH_CHAT,text=text)