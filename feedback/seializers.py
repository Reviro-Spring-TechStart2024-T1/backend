from rest_framework import serializers
from .models import Feedback
from establishments.models import Establishment
from accounts.models import User


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class EstablishmentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = ['id', 'name']


class FeedbackSerializer(serializers.ModelSerializer):
    user_name = UserNameSerializer(read_only=True)
    establishment = EstablishmentNameSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id',
            'user',
            'user_name',
            'establishment',
            'rating',
            'comment'
        ]
        extra_kwargs = {
            'user': {'write_only': True},
            'establishment': {'write_only': True}
        }

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.role != 'customer':
                raise serializers.ValidationError("Only customers can leave feedback.")
        return data
