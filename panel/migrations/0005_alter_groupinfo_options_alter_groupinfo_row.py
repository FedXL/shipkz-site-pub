# Generated by Django 5.1.1 on 2025-01-03 01:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0004_rename_rowinfo_groupinfo_alter_groupinfo_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupinfo',
            options={'verbose_name': 'Info', 'verbose_name_plural': 'Row Info'},
        ),
        migrations.AlterField(
            model_name='groupinfo',
            name='row',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='row_info', to='panel.ordersgroup'),
        ),
    ]
