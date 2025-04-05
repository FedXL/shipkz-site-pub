# Generated by Django 5.1.1 on 2025-03-25 13:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legacy', '0005_alter_orderstatusinfo_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderstatus',
            options={'managed': False, 'verbose_name': 'Tradeinn Информация о заказе'},
        ),
        migrations.AlterModelOptions(
            name='orderstatusinfo',
            options={'managed': False, 'verbose_name': 'Транзит информация о заказе', 'verbose_name_plural': 'Транзит информация о заказах'},
        ),
        migrations.AlterModelOptions(
            name='users',
            options={'managed': False, 'verbose_name': 'Телеграм пользователь'},
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='legacy.orders'),
        ),
    ]
