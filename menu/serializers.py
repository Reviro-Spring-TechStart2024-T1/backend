from rest_framework import serializers
from establishments.models import Establishment
from .models import ItemCategory, Menu, MenuItem


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name']


class MenuSerializer(serializers.ModelSerializer):
    establishment = serializers.PrimaryKeyRelatedField(queryset=Establishment.objects.all())

    class Meta:
        model = Menu
        fields = [
            'id',
            'establishment',
            'created_at',
            'updated_at',
            'qr_code_image'
        ]


class MenuItemSerializer(serializers.ModelSerializer):
    item_category = serializers.PrimaryKeyRelatedField(queryset=ItemCategory.objects.all())
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())

    class Meta:
        model = MenuItem
        fields = [
            'id',
            'menu',
            'name',
            'item_category',
            'price',
            'description',
            'availability_status',
            'happy_hour_start',
            'happy_hour_end'
        ]