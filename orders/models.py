from django.db import models
from accounts.models import User
from establishments.models import Establishment
from menu.models import MenuItem
from django.utils import timezone


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="orders")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.pk} by {self.user.email} at {self.establishment.name} - {self.menu_item.name}"
