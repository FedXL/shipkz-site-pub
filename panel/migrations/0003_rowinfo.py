import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legacy', '0005_alter_orderstatusinfo_options'),
        ('panel', '0002_create_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='RowInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_reward', models.CharField(blank=True, max_length=255, null=True)),
                ('shop', models.CharField(blank=True, max_length=255, null=True)),
                ('order_sum', models.CharField(blank=True, max_length=255, null=True)),
                ('order_currency', models.CharField(blank=True, max_length=255, null=True)),
                ('store_order_number', models.CharField(blank=True, max_length=255, null=True)),
                ('is_forward', models.BooleanField(default=False, verbose_name='Заказ через форвардера')),
                ('forward_name', models.CharField(blank=True, max_length=255, null=True)),
                ('post_service', models.CharField(blank=True, max_length=50, null=True, verbose_name='Почтовая служба')),
                ('trek', models.CharField(blank=True, max_length=255, null=True)),
                ('estimated_date_of_arrival', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ориентировочная дата прибытия КЗ')),
                ('payment_card', models.CharField(blank=True, max_length=255, null=True, verbose_name='Карта для оплаты')),
                ('is_delivery_payment', models.BooleanField(default=False, verbose_name='Оплачена ли доставка в РФ')),
                ('comment', models.CharField(blank=True, null=True)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='row_buyer', to='legacy.buyers')),
                ('row', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='row_info', to='panel.ordersgroup')),
            ],
        ),
    ]
