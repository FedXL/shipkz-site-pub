from django.db.models.signals import post_save
from django.dispatch import receiver
from app_front.management.email.email_sender import my_logger
from panel.models import OrdersGroup
from legacy.models import Orders


@receiver(post_save, sender=Orders)
def update_order_status(sender, instance, created, **kwargs):
    my_logger.info('START ORDER SIGNAL')
    my_logger.info(f'instance: {instance}')

    # Срабатывает только при создании
    if created and instance.type in ['KAZ_ORDER_LINKS', 'PAYMENT', 'WEB_ORDER']:
        try:
            group = instance.group
            if not group:
                order_group = OrdersGroup.objects.create()
                instance.group = order_group
                instance.save()
        except Exception as ER:
            my_logger.error(f"Ошибка при создании группы заказов: {ER}")