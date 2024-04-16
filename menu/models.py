from django.db import models
from establishments.models import Establishment


class ItemCategory(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Item Category"
        verbose_name_plural = "Item Categories"

    def __str__(self):
        return self.name


class Menu(models.Model):
    establishment = models.OneToOneField(Establishment, on_delete=models.CASCADE, related_name="menu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code_image = models.ImageField(upload_to='menu/qr_code_images/', blank=True, null=True)

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    def __str__(self):
        return f"Menu of the {self.establishment.name}"


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name='menu_items')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    availability_status = models.BooleanField()
    happy_hour_start = models.TimeField(null=True, blank=True)
    happy_hour_end = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return self.name
