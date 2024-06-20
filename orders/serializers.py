from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import exceptions, serializers

from accounts.models import User
from menu.models import Beverage, Menu
from subscriptions.models import UserSubscription

from .models import Order


class CustomerOrderSerializer(serializers.ModelSerializer):
    '''
    For customers to create and view their orders
    '''
    beverage_id = serializers.IntegerField(write_only=True)
    establishment_name = serializers.CharField(source='menu.establishment.name', read_only=True)
    beverage_name = serializers.CharField(source='beverage.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'establishment_name',
            'beverage_id',
            'beverage_name',
            'order_date',
            'status',
            'quantity',
            'last_updated'
        ]
        read_only_fields = [
            'id',
            'establishment_name',
            'beverage_name',
            'order_date',
            'status',
            'last_updated',
            'quantity',  # default = 1
        ]

    def is_within_happy_hour(self, happy_hour_start, happy_hour_end, current_time):
        if happy_hour_start <= happy_hour_end:
            # Happy hour within the same day
            return happy_hour_start <= current_time <= happy_hour_end
        else:
            # Happy hour spanning across midnight
            return current_time >= happy_hour_start or current_time <= happy_hour_end

    def create(self, validated_data):
        beverage_id = validated_data['beverage_id']
        user = self.context['request'].user
        current_time = timezone.localtime(timezone.now())
        current_time_only = current_time.time()

        if beverage_id is None:
            raise serializers.ValidationError({'error': 'Beverage ID is required.'})

        try:
            beverage = Beverage.objects.get(id=beverage_id)
            menu = Menu.objects.get(id=beverage.menu.id)
            establishment = menu.establishment

            # Check if the user has an active subscription
            subscription = UserSubscription.objects.get(user=user)
            if subscription.status != 'ACTIVE':
                raise exceptions.PermissionDenied('Your subscription is not active. Please renew your subscription.')
        except UserSubscription.DoesNotExist:
            raise exceptions.PermissionDenied('No subscription found. Please subscribe to use this service.')

        except Beverage.DoesNotExist:
            raise serializers.ValidationError({'error': 'Beverage with given ID does not exist.'})
        except Menu.DoesNotExist:
            raise serializers.ValidationError({'error': 'Menu for the given beverage does not exist.'})

        happy_hour_start = establishment.happy_hour_start
        happy_hour_end = establishment.happy_hour_end

        if self.is_within_happy_hour(happy_hour_start, happy_hour_end, current_time_only):
            # Check if the user has already ordered a free beverage at this establishment during the day
            if Order.objects.filter(
                user=user,
                menu=menu,
                order_date__date=current_time.date()
            ).exists():
                raise serializers.ValidationError(
                    {'error': 'You have already claimed a free beverage at this establishment today.'}
                )
        else:
            raise serializers.ValidationError(
                {'error': f'It is not happy hour currently. '
                 f'Please order within establishment happy hours: {happy_hour_start} to {happy_hour_end}'}
            )

        order = Order.objects.create(
            beverage=beverage,
            user=user,
            menu=menu,
            status='pending'
        )

        return order


class PartnersCreateOrderSerializer(serializers.ModelSerializer):
    '''
    Allow partners to create orders for customers by posting beverage_id and customer_id
    '''
    beverage_id = serializers.IntegerField(write_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    establishment_name = serializers.CharField(source='menu.establishment.name', read_only=True)
    beverage_name = serializers.CharField(source='beverage.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'establishment_name',
            'beverage_id',
            'customer_id',
            'beverage_name',
            'order_date',
            'status',
            'quantity',
            'last_updated'
        ]
        read_only_fields = [
            'id',
            'establishment_name',
            'beverage_name',
            'order_date',
            'status',
            'last_updated',
            'quantity',  # defaults to 1
        ]

    def create(self, validated_data):
        beverage_id = validated_data['beverage_id']
        customer_id = validated_data['customer_id']

        if beverage_id is None:
            raise serializers.ValidationError({'error': 'Beverage ID is required.'})

        try:
            beverage = Beverage.objects.get(id=beverage_id)
            menu = Menu.objects.get(id=beverage.menu.id)
            customer = User.objects.get(id=customer_id, role='customer')
        except Beverage.DoesNotExist:
            raise serializers.ValidationError({'error': 'Beverage with given ID does not exist.'})
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': 'Customer with given ID does not exist.'})

        order = Order.objects.create(
            beverage=beverage,
            user=customer,
            menu=menu,
            status='pending'
        )

        return order


class PartnersDetailOrderSerializer(serializers.ModelSerializer):
    '''
    Allow partners to view and update order details
    '''
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    establishment_name = serializers.CharField(source='menu.establishment.name', read_only=True)
    beverage_name = serializers.CharField(source='beverage.name', read_only=True)
    beverage_price = serializers.DecimalField(source='beverage.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user_email',
            'user_first_name',
            'user_last_name',
            'establishment_name',
            'beverage_name',
            'beverage_price',
            'order_date',
            'status',
            'quantity',
            'last_updated'
        ]
        read_only_fields = [
            'id',
            'user_email',
            'user_first_name',
            'user_last_name',
            'establishment_name',
            'beverage_name',
            'beverage_price',
            'order_date',
            'quantity',
            'last_updated'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'sex', 'date_of_birth', ]


class FindCustomerByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class OrderHistorySerializer(serializers.ModelSerializer):
    beverage_name = serializers.CharField(source='beverage.name', read_only=True)
    price = serializers.DecimalField(source='beverage.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_date', 'beverage_name', 'price']


class DetailedCustomerProfileSerializer(serializers.ModelSerializer):
    '''
    This serializer nests the OrderHistorySerializer to include order details specific to the partner’s establishment.
    '''
    orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'sex',
            'date_of_birth',
            'orders'
        ]

    @extend_schema_field(OrderHistorySerializer(many=True))
    def get_orders(self, obj):
        request = self.context.get('request')
        user = request.user
        orders = Order.objects.filter(beverage__menu__establishment__owner=user, user=obj)
        return OrderHistorySerializer(orders, many=True).data


class DayStatisticsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    sum = serializers.IntegerField()


class WeekStatisticsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    sum = serializers.IntegerField()


class MonthStatisticsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    sum = serializers.IntegerField()


class QuarterStatisticsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    sum = serializers.IntegerField()


class YearStatisticsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    sum = serializers.IntegerField()


class OrderStatisticsSerializer(serializers.Serializer):
    this_week = serializers.DictField(child=DayStatisticsSerializer())
    last_week = serializers.DictField(child=DayStatisticsSerializer())
    this_month = serializers.DictField(child=WeekStatisticsSerializer())
    last_month = serializers.DictField(child=WeekStatisticsSerializer())
    this_quarter = serializers.DictField(child=MonthStatisticsSerializer())
    last_quarter = serializers.DictField(child=MonthStatisticsSerializer())
    this_year = serializers.DictField(child=QuarterStatisticsSerializer())
    last_year = serializers.DictField(child=QuarterStatisticsSerializer())
