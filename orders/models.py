from django.db import models
from django.utils import timezone

from accounts.models import User
from core.models import BaseModel, BaseModelManager
from establishments.models import Establishment
from menu.models import Beverage


class Order(BaseModel):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name='orders')
    beverage = models.ForeignKey(Beverage, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    objects = BaseModelManager()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.pk} by {self.user.email} at {self.establishment.name} - {self.beverage.name}"
