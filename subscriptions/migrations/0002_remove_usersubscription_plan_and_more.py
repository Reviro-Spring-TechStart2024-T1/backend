# Generated by Django 5.0.4 on 2024-06-11 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersubscription',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='usersubscription',
            name='user',
        ),
        migrations.DeleteModel(
            name='SubscriptionPlan',
        ),
        migrations.DeleteModel(
            name='UserSubscription',
        ),
    ]
