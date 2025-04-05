from django.db import migrations
from legacy.models import Orders
from panel.models import OrdersGroup

def create_orders_group(apps, schema_editor):
    for order in Orders.objects.all():
        print(order.id)
        order_group_obj = order.group

        if not order_group_obj:
            order_group_obj = OrdersGroup.objects.create(group_name=order.id)
            order.group = order_group_obj
            order.save()

class Migration(migrations.Migration):
    dependencies = [
        ('panel', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_orders_group),
    ]