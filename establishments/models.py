from django.core.validators import RegexValidator
from django.db import models

from accounts.models import User
from core.models import BaseModel


class Establishment(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'partner'})
    name = models.CharField(max_length=255)
    email = models.EmailField()
    street_name = models.CharField(max_length=255, null=True, blank=True)
    street_number = models.CharField(max_length=10, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    description = models.TextField(blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+996-[0-9]{3}-[0-9]{6}$',
        message="Phone number must be entered in the format: '+996-XXX-XXXXXX'.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    logo = models.ImageField(upload_to='establishments/logos/', null=True, blank=True)
    happy_hour_start = models.TimeField(null=True, blank=True)
    happy_hour_end = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Establishment'
        verbose_name_plural = 'Establishments'

    def __str__(self):
        return self.name


class EstablishmentBanner(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name='banners')
    url = models.ImageField(upload_to='establishments/banners/')

    class Meta:
        verbose_name = 'Establishment Banner'
        verbose_name_plural = 'Establishment Banners'

    def __str__(self):
        return f'Banner for {self.establishment.name}'
