from rest_framework import serializers

from menu.models import Beverage, Menu

from .models import Order


class UsersOrderSerializer(serializers.ModelSerializer):
    beverage_id = serializers.IntegerField(write_only=True)
    establishment_name = serializers.CharField(source='menu.establishment.name', read_only=True)
    beverage_name = serializers.CharField(source='beverage.name', read_only=True)
    beverage_price = serializers.DecimalField(source='beverage.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'establishment_name',
            'beverage_id',
            'beverage_name',
            'beverage_price',
            'order_date',
            'status',
            'quantity',
            'last_updated'
        ]
        read_only_fields = [
            'id',
            'establishment_name',
            'beverage_name',
            'beverage_price',
            'order_date',
            'status',
            'last_updated',
            'quantity',  # defaults to 1
        ]

    def create(self, validated_data):
        beverage_id = validated_data['beverage_id']

        if beverage_id is None:
            raise serializers.ValidationError({'error': 'Beverage ID is required.'})

        try:
            beverage = Beverage.objects.get(id=beverage_id)
            menu = Menu.objects.get(id=beverage.menu.id)
        except Beverage.DoesNotExist:
            raise serializers.ValidationError({'error': 'Beverage with given ID does not exist.'})

        user = self.context['request'].user

        order = Order.objects.create(
            beverage=beverage,
            user=user,
            menu=menu
        )

        return order


class PartnersOrderSerializer(serializers.ModelSerializer):
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
        read_only_fields = ['quantity', 'order_date', 'last_updated']
