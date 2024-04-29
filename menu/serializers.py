from rest_framework import serializers

from establishments.models import Establishment

from .models import Beverage, Category, Menu, QrCode


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class BeverageSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())

    class Meta:
        model = Beverage
        fields = [
            'id',
            'menu',
            'name',
            'category',
            'price',
            'description',
            'in_stock'
        ]


class MenuSerializer(serializers.ModelSerializer):
    establishment = serializers.PrimaryKeyRelatedField(queryset=Establishment.objects.all())
    beverages = BeverageSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = [
            'id',
            'establishment',
            'created_at',
            'updated_at',
            'beverages'
        ]


class QrCodeSerializer(serializers.ModelSerializer):
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())
    qr_code_image = serializers.ImageField(max_length=None, use_url=True, required=False, allow_null=True)

    class Meta:
        model = QrCode
        fields = [
            'id',
            'menu',
            'qr_code_image',
            'created_at',
            'updated_at'
        ]
