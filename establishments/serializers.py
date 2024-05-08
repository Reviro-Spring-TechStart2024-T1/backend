from rest_framework import serializers

from accounts.models import User

from .models import Establishment, EstablishmentBanner


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

    class Meta:
        model = Establishment
        fields = [
            'id',
            'owner',
            'name',
            'email',
            'street_name',
            'street_number',
            'latitude',
            'longitude',
            'description',
            'phone_number',
            'logo',
            'banners',
            'happy_hour_start',
            'happy_hour_end'
        ]
