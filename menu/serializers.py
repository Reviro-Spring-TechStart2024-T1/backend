from rest_framework import serializers

from establishments.models import Establishment

from .models import ItemCategory, Menu, MenuItem, QrCode


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
            'updated_at'
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
            'in_stock'
        ]


class QrCodeSerializer(serializers.ModelSerializer):
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())
    qr_code_image = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = QrCode
        fields = [
            'id',
            'menu',
            'qr_code_image',
            'created_at',
            'updated_at'
        ]
