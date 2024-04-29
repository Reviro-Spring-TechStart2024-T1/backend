from rest_framework import serializers

from accounts.models import User
from establishments.models import Establishment
from menu.models import Beverage

from .models import Order


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class EstablishmentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = ['id', 'name']


class BeverageOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beverage
        fields = ['id', 'name']


class OrderSerializer(serializers.ModelSerializer):
    user_email = UserEmailSerializer(read_only=True)
    establishment_name = EstablishmentOrderSerializer(read_only=True)
    beverage_name = BeverageOrderSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_email',
            'establishment_name',
            'beverage',
            'beverage_name',
            'order_date',
            'status',
            'quantity',
            'last_updated'
        ]
        read_only_fields = ['last_updated']
