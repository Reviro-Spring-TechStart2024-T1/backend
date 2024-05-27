from datetime import timedelta

from django.db import models
from django.utils import timezone

from accounts.models import User


class SubscriptionPlan(models.Model):
    DURATION_CHOICES = [
        (30, '1 Month'),
        (90, '3 Months'),
        (180, '6 Months'),
        (365, '1 Year')
    ]

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    free_trial_days = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.end_date:
            trial_days = self.plan.free_trial_days if self.is_trial else 0
            self.end_date = self.start_date + timedelta(days=self.plan.duration + trial_days)
        super().save(*args, **kwargs)

    def extend_subscription(self, additional_days):
        self.end_date += timedelta(days=additional_days)
        self.save()

    def cancel_subscription(self):
        self.is_active = False
        self.save()

    def remaining_days(self):
        if self.end_date and self.is_active:
            return (self.end_date - timezone.now()).days
        return 0

    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'

    def __str__(self):
        return f'{self.user.email} - {self.plan.name}'