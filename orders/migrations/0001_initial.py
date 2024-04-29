# Generated by Django 5.0.4 on 2024-04-29 09:25

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('establishments', '0001_initial'),
        ('menu', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending', max_length=10)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('beverage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='menu.beverage')),
                ('establishment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='establishments.establishment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
