# Generated by Django 5.1.1 on 2025-01-02 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legacy', '0005_alter_orderstatusinfo_options'),
        ('panel', '0003_rowinfo'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RowInfo',
            new_name='GroupInfo',
        ),
        migrations.AlterModelOptions(
            name='groupinfo',
            options={'verbose_name': 'Info', 'verbose_name_plural': 'Info'},
        ),
    ]
