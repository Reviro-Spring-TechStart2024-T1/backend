# Generated by Django 5.0.4 on 2024-05-21 09:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('establishments', '0002_alter_establishment_owner'),
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='establishment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='menus', to='establishments.establishment'),
        ),
    ]
