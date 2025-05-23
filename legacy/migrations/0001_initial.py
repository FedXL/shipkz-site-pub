# Generated by Django 5.1.1 on 2024-12-18 23:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Buyers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.BigIntegerField(blank=True, null=True)),
                ('telegram_id', models.BigIntegerField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('second_name', models.CharField(blank=True, max_length=50, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'buyers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Discounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_vip', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'discounts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_id', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'documents',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EmailTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('header', models.CharField(max_length=255)),
                ('execute_time', models.DateTimeField()),
                ('status', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'email_task',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('valuta', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('price', models.FloatField(blank=True, null=True)),
                ('data', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'exchange',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='FastAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(blank=True, null=True)),
                ('button_name', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'fast_answers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Jwt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jwt_hash', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'jwt',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Managers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(blank=True, max_length=255, null=True)),
                ('key', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'managers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_body', models.TextField(blank=True, null=True)),
                ('is_answer', models.BooleanField(blank=True, null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('message_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'messages',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('body', models.TextField(blank=True, null=True)),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('user_ip', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'orders',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(blank=True, null=True)),
                ('order_price', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'order_status',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OrderStatusInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_forward', models.BooleanField()),
                ('forward_name', models.CharField(blank=True, max_length=255, null=True)),
                ('paid', models.DateTimeField()),
                ('arrived_to_forward', models.DateTimeField(blank=True, null=True)),
                ('got_track', models.DateTimeField(blank=True, null=True)),
                ('arrived_to_host_country', models.DateTimeField(blank=True, null=True)),
                ('received_in_host_country', models.DateTimeField(blank=True, null=True)),
                ('send_to_ru', models.DateTimeField(blank=True, null=True)),
                ('success', models.DateTimeField(blank=True, null=True)),
                ('relative_price', models.CharField(blank=True, max_length=255, null=True)),
                ('buyer_reward', models.CharField(blank=True, max_length=255, null=True)),
                ('shop', models.CharField(blank=True, max_length=255, null=True)),
                ('store_order_number', models.CharField(max_length=255)),
                ('trek', models.CharField(blank=True, max_length=255, null=True)),
                ('cdek', models.CharField(blank=True, max_length=255, null=True)),
                ('estimated_date_of_arrival', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ориентировочная дата прибытия КЗ')),
                ('post_service', models.CharField(blank=True, max_length=50, null=True)),
                ('host_country', models.CharField(blank=True, max_length=255, null=True)),
                ('buyer', models.BigIntegerField(blank=True, null=True)),
                ('payment_card', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'order_status_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ParceTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(blank=True, max_length=255, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'parce_task',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Photos',
            fields=[
                ('photo_id', models.AutoField(primary_key=True, serialize=False)),
                ('file_id', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'photos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('message_id', models.BigIntegerField(blank=True, null=True)),
                ('chat_id', models.BigIntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
            ],
            options={
                'db_table': 'posts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RootUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'root_users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('service_name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('status', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('report', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'services',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(blank=True, max_length=255, null=True)),
                ('message_id', models.IntegerField(blank=True, null=True)),
                ('tele_username', models.CharField(blank=True, max_length=50, null=True)),
                ('user_second_name', models.CharField(blank=True, max_length=50, null=True)),
                ('main_user', models.IntegerField(blank=True, null=True)),
                ('is_kazakhstan', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UsersApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'users_app',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WebDocs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_path', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'web_docs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WebMessages',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('message_body', models.CharField(blank=True, max_length=255, null=True)),
                ('is_answer', models.BooleanField(blank=True, null=True)),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
                ('message_type', models.CharField(blank=True, max_length=255, null=True)),
                ('is_read', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'web_messages',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WebPhotos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo_path', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'web_photos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Websockets',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('socket_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'websockets',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WebsocketsSupport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('socket_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'websockets_support',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WebUsers',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(blank=True, max_length=255, null=True)),
                ('web_username', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('is_kazakhstan', models.BooleanField(blank=True, default=True, null=True)),
                ('last_online', models.DateTimeField(blank=True, null=True)),
                ('last_message_telegramm_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'web_users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WebUsersMeta',
            fields=[
                ('meta_id', models.AutoField(primary_key=True, serialize=False)),
                ('field', models.CharField(max_length=255)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'web_users_meta',
                'managed': False,
            },
        ),
    ]
