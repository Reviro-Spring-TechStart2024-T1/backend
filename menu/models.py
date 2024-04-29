from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from rest_framework.reverse import reverse

from establishments.models import Establishment

from .utils import generate_qr_code


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Menu(models.Model):
    establishment = models.OneToOneField(Establishment, on_delete=models.CASCADE, related_name='menu')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return f'Menu of the {self.establishment.name}'


class Beverage(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='beverages')
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='beverages')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    in_stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Beverage'
        verbose_name_plural = 'Beverages'

    def __str__(self):
        return self.name


class QrCode(models.Model):
    menu = models.OneToOneField(Menu, on_delete=models.CASCADE, related_name='qrcode')
    qr_code_image = models.ImageField(upload_to='menu/qr_code_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.qr_code_image:
            # f'https//drinkjoy.com/menu/{self.menu.id}/details'
            data = 'https://{}{}'.format(settings.ALLOWED_HOSTS[0],
                                         reverse('menu-detail', args=[self.menu.id]))  # type: ignore
            buffer = generate_qr_code(data)
            filename = f'qrcode-{self.menu.id}.png'

            # Saving the image from buffer to the Imagefield
            self.qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'QR code'
        verbose_name_plural = 'QR codes'

    def __str__(self):
        return f'QR code of {self.menu}'
