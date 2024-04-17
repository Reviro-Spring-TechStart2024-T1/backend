from rest_framework import serializers
from .models import Order
from accounts.models import User
from establishments.models import Establishment
from menu.models import MenuItem


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class EstablishmentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = ['id', 'name']


class MenuItemOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name']


class OrderSerializer(serializers.ModelSerializer):
    user_email = UserEmailSerializer(read_only=True)
    establishment_name = EstablishmentOrderSerializer(read_only=True)
    menu_item_name = MenuItemOrderSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_email',
            'establishment_name',
            'menu_item',
            'menu_item_name',
            'order_date',
            'status',
            'quantity',
            'last_updated'
        ]
        read_only_fields = ['last_updated']
