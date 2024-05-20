from datetime import datetime, timedelta

import django_filters
from django.utils import timezone

from .models import Order


class CustomBaseFilterSet(django_filters.FilterSet):
    time = django_filters.CharFilter(method='filter_by_time')

    def filter_by_time(self, queryset, name, value):
        now = timezone.now()

        if value == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif value == 'yesterday':
            end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=1)
        elif value == 'this_month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = start_date + timedelta(days=31)
            end_date = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif value == 'last_month':
            first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = first_of_this_month
            start_date = (first_of_this_month - timedelta(days=1)).replace(day=1,
                                                                           hour=0, minute=0, second=0, microsecond=0)
        elif value == 'last_6_months':
            start_date = (now - timedelta(days=180)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif value == 'this_year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)
        elif value == 'last_year':
            start_date = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(year=now.year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # If the provided value does not match any of the options, return the original queryset
            return queryset

        return queryset.filter(order_date__gte=start_date, order_date__lt=end_date)


class PartnersOrdersListCustomFilter(CustomBaseFilterSet):
    order_date = django_filters.CharFilter(method='filter_by_order_date')

    class Meta:
        model = Order
        fields = [
            'order_date',
            'id',
            'status',
            'beverage__name'
        ]

    def filter_by_order_date(self, queryset, name, value):
        try:
            # Parse the input date
            input_date = datetime.strptime(value, '%Y-%m-%d')
            start_date = timezone.make_aware(input_date)
            end_date = timezone.make_aware(input_date + timedelta(days=1))
            # Filter queryset for orders made on the specified date
            return queryset.filter(order_date__gte=start_date, order_date__lt=end_date)
        except ValueError:
            # If the date format is invalid, return an empty queryset or handle as needed
            return queryset.none()


class UsersOrderListCustomFilter(CustomBaseFilterSet):
    class Meta:
        model = Order
        fields = [
            'status'
        ]
