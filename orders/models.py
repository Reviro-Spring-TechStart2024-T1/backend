from django.db import models
from django.utils import timezone

from accounts.models import User
from core.models import BaseModel
from menu.models import Beverage, Menu


class Order(BaseModel):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='orders')
    beverage = models.ForeignKey(Beverage, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order {self.pk} by {self.user.email} at {self.menu.establishment.name} - {self.beverage.name}'
