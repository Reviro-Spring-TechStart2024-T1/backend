import os

import geocoder
from dotenv import load_dotenv
from rest_framework import serializers

from accounts.models import User
from menu.models import Menu

from .models import Establishment, EstablishmentBanner

load_dotenv()


class EstablishmentBannerSerializer(serializers.ModelSerializer):
    url = serializers.ImageField()

    class Meta:
        model = EstablishmentBanner
        fields = [
            'id',
            'establishment',
            'url'
        ]

    def validate_establishment(self, value):
        if not Establishment.objects.filter(id=value.id).exists():
            raise serializers.ValidationError('Establishment not found with the given ID.')
        return value


class EstablishmentSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='partner'))
    banners = EstablishmentBannerSerializer(many=True, read_only=True)
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), required=False)

    class Meta:
        model = Establishment
        fields = [
            'id',
            'owner',
            'name',
            'email',
            'address',
            'location',
            'description',
            'phone_number',
            'logo',
            'banners',
            'happy_hour_start',
            'happy_hour_end',
            'menu'
        ]
        read_only_fields = [
            'location',
        ]

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        g = geocoder.google(address_data, key=os.environ.get('GOOGLE_MAPS_KEY'))
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        point = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'
        instance.location = point

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance
