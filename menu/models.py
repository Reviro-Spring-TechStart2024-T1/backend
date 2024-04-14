from django.db import models
from establishments.models import Establishment, Category


class MenuItem(models.Model):
    """ AKA Beverage, this model name hasn't been confirmed"""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
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


class Menu(models.Model):
    establishment = models.OneToOneField(Establishment, on_delete=models.CASCADE, related_name="menu")
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    def __str__(self):
        return self.establishment.name


class MenuMenuItem(models.Model):
    """ This is not confirmed model name, we can change it to MenuEntry"""
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_entries")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="menu_entries")

    def __str__(self):
        return f"{self.menu_item} of the {self.menu}"
