from django.db import models

from core.models import BaseModel
from establishments.models import Establishment


class Category(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Menu(BaseModel):
    establishment = models.OneToOneField(Establishment, on_delete=models.CASCADE, related_name='menus')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return f'{self.id}'


class Beverage(BaseModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='beverages')
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='beverages', null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    in_stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Beverage'
        verbose_name_plural = 'Beverages'

    def __str__(self):
        return f'{self.id}'
