from rest_framework import serializers

from accounts.models import User

from .models import Establishment


class EstablishmentSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='partner'))

    class Meta:
        model = Establishment
        fields = [
            'id',
            'owner',
            'name',
            'email',
            'latitude',
            'longitude',
            'description',
            'phone_number',
            'logo',
            'banner_image',
            'happy_hour_start',
            'happy_hour_end'
        ]
