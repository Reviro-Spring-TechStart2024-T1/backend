from django.db import models
from accounts.models import User
from django.core.validators import RegexValidator


class Establishment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'partner'})
    name = models.CharField(max_length=255)
    email = models.EmailField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    description = models.TextField(blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+996-[0-9]{3}-[0-9]{6}$',
        message="Phone number must be entered in the format: '+996-XXX-XXXXXX'."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    logo = models.ImageField(upload_to='establishments/logos/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='establishments/banners/', null=True, blank=True)

    class Meta:
        verbose_name = "Establishment"
        verbose_name_plural = "Establishments"

    def __str__(self):
        return self.name
