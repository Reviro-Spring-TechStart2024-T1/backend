# Generated by Django 5.0.4 on 2024-04-17 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('not_say', 'Prefer not to say')], default='not_say', max_length=10),
        ),
    ]
