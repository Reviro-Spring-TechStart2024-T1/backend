# Generated by Django 5.0.4 on 2024-05-07 08:50

import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_alter_category_managers'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='beverage',
            managers=[
                ('everything', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='menu',
            managers=[
                ('everything', django.db.models.manager.Manager()),
            ],
        ),
    ]
