# Generated by Django 5.0.4 on 2024-06-11 07:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_remove_usersubscription_plan_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypalsubscriptionplan',
            name='price',
            field=models.CharField(blank=True, max_length=32, null=True, validators=[django.core.validators.RegexValidator(message='As string enter a valid positive integer or decimal number.', regex='^(([0-9]+)|([0-9]+[.][0-9]+))$')]),
        ),
    ]