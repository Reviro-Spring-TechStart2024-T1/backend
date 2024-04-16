from rest_framework import serializers
from .models import Establishment
from accounts.models import User


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
            'banner_image'
        ]
