from rest_framework import serializers

from establishments.models import Establishment

from .models import Beverage, Category, Menu


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class BeverageSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())

    class Meta:
        model = Beverage
        fields = ['id', 'menu', 'name', 'category', 'price', 'description', 'in_stock']


class MenuSerializer(serializers.ModelSerializer):
    establishment = serializers.PrimaryKeyRelatedField(
        queryset=Establishment.objects.all()
    )
    beverages = BeverageSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ['id', 'establishment', 'created_at', 'updated_at', 'beverages']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get('request')
        if request:
            beverage_name = request.query_params.get('beverage__name')
            if beverage_name:
                beverages = instance.beverages.filter(name__icontains=beverage_name)
                beverage_serializer = BeverageSerializer(beverages, many=True, context=self.context)
                representation['beverages'] = beverage_serializer.data

        return representation
