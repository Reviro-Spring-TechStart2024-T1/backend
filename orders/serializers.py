from django.utils import timezone
from rest_framework import serializers

from accounts.models import User
from menu.models import Beverage, Menu

from .models import Order


class UsersOrderSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        beverage_id = validated_data['beverage_id']
        user = self.context['request'].user
        current_time = timezone.now()

        if beverage_id is None:
            raise serializers.ValidationError({'error': 'Beverage ID is required.'})

        try:
            beverage = Beverage.objects.get(id=beverage_id)
            menu = Menu.objects.get(id=beverage.menu.id)
            establishment = menu.establishment
        except Beverage.DoesNotExist:
            raise serializers.ValidationError({'error': 'Beverage with given ID does not exist.'})

        if establishment.happy_hour_start <= current_time.time() <= establishment.happy_hour_end:
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
                {'error': 'It is not happy hour currently. Please order within establishment happy hours'}
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
