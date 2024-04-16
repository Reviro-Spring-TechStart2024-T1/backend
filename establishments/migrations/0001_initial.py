# Generated by Django 5.0.4 on 2024-04-16 08:15

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Establishment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('latitude', models.DecimalField(decimal_places=8, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=8, max_digits=11)),
                ('description', models.TextField(blank=True)),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+996-XXX-XXXXXX'.", regex='^\\+996-[0-9]{3}-[0-9]{6}$')])),
                ('logo', models.ImageField(blank=True, null=True, upload_to='establishments/logos/')),
                ('owner', models.ForeignKey(limit_choices_to={'role': 'partner'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Establishment',
                'verbose_name_plural': 'Establishments',
            },
        ),
    ]
