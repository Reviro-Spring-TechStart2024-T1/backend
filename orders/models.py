from django.db import models
from accounts.models import User
from establishments.models import Establishment
from menu.models import MenuItem
from django.utils import timezone
# from django.core.exceptions import ValidationError


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="orders")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField(default=timezone.now)

    # def clean(self):
    #     if self.user.role != "customer":
    #         raise ValidationError("Only customers can place orders.")
    #
    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.pk} by {self.user.email} at {self.establishment.name} ordered {self.menu_item.name}"
