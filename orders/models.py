from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone

from accounts.models import User
from core.models import BaseModel
from menu.models import Beverage, Menu


class OrderManager(models.Manager):
    def for_partner(self, partner):
        return self.filter(
            menu__establishment__owner=partner
        ).select_related('beverage')

    def get_stats_by_day(self, partner, start_date, end_date):
        orders_by_day = {}
        current_day = start_date

        while current_day <= end_date:
            orders = self.for_partner(partner).filter(order_date__date=current_day)
            orders_total_count = orders.count()
            orders_total_sum = orders.aggregate(total_sum=models.Sum('beverage__price'))['total_sum'] or 0
            orders_by_day[current_day.strftime('%a-%Y-%m-%d')] = {
                'count': orders_total_count,
                'sum': orders_total_sum
            }
            current_day += timedelta(days=1)

        return orders_by_day

    def get_stats_by_week(self, partner, start_date, end_date):
        orders_by_week = {}
        current_week_start = start_date

        while current_week_start <= end_date:
            current_week_end = current_week_start + timedelta(days=6)
            if current_week_end > end_date:
                current_week_end = end_date
            week_orders = self.for_partner(partner).filter(
                order_date__date__range=[current_week_start, current_week_end])
            week_orders_count = week_orders.count()
            week_orders_sum = week_orders.aggregate(total_sum=models.Sum('beverage__price'))['total_sum'] or 0
            orders_by_week[
                (str(current_week_start.strftime('%a-%Y-%m-%d')) + ' - ' +  # noqa: W504
                 str(current_week_end.strftime('%a-%Y-%m-%d')))
            ] = {
                'count': week_orders_count,
                'sum': week_orders_sum
            }

            current_week_start += timedelta(days=7)

        return orders_by_week

    def get_stats_by_month(self, partner, start_date, end_date):
        orders_by_month = {}
        current_month_start = start_date

        while current_month_start <= end_date:
            current_month_end = (current_month_start + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
            if current_month_end > end_date:
                current_month_end = end_date
            month_data = self.get_stats_by_week(partner, current_month_start, current_month_end)
            month_count = sum(week_data['count'] for week_data in month_data.values())
            month_sum = sum(week_data['sum'] for week_data in month_data.values())
            orders_by_month[current_month_start.strftime('%Y-%m')] = {
                'count': month_count,
                'sum': month_sum
            }
            current_month_start += relativedelta(months=1)

        return orders_by_month

    def get_stats_by_quarter(self, partner, start_date, end_date):
        orders_by_quarter = {}
        current_quarter_start = self.get_start_of_quarter(start_date)

        while current_quarter_start <= end_date:
            current_quarter_end = current_quarter_start + relativedelta(months=3, days=-1)
            if current_quarter_end > end_date:
                current_quarter_end = end_date
            quarter_data = self.get_stats_by_month(partner, current_quarter_start, current_quarter_end)
            quarter_count = sum(month_data['count'] for month_data in quarter_data.values())
            quarter_sum = sum(month_data['sum'] for month_data in quarter_data.values())
            quarter_label = f'Q{(current_quarter_start.month - 1) // 3 + 1}_{current_quarter_start.year}'
            orders_by_quarter[quarter_label] = {
                'count': quarter_count,
                'sum': quarter_sum
            }
            current_quarter_start += relativedelta(months=3)

        return orders_by_quarter

    def get_start_of_quarter(self, date):
        quarter_month = (date.month - 1) // 3 * 3 + 1
        return datetime(date.year, quarter_month, 1, tzinfo=date.tzinfo)


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

    statistics = OrderManager()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order {self.pk} by {self.user.email} at {self.menu.establishment.name} - {self.beverage.name}'
