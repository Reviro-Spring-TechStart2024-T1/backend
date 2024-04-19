import re

from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class PasswordMixin(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': "Password fields didn't match."})

        password = attrs['password']
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({'password': 'Password must contain at least one uppercase letter.'})
        if not re.search(r'[!@#$%^&*]', password):
            raise serializers.ValidationError(
                {'password': 'Password must contain at least one special character (!@#$%^&*).'})
        if len(password) < 8:
            raise serializers.ValidationError({'password': 'Password must be at least 8 characters long.'})
        return attrs


class UserRegisterSerializer(serializers.ModelSerializer, PasswordMixin):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'confirm_password'
        ]

    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    # def to_representation(self, instance):
    # """Extra method if needed: Return limited data upon registration"""
    #     return {
    #         'id': instance.id,
    #         'email': instance.email
    #     }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'avatar', 'sex', 'date_of_birth']

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'role',
            'date_of_birth',
            'email',
            'sex'
        ]


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = User
        fields = [
            'email',
            'password',
        ]


class ChangePasswordSerializer(serializers.ModelSerializer, PasswordMixin):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError({'error': 'Invalid old password.'})
        return value

    class Meta:
        model = User
        fields = ['old_password', 'password', 'confirm_password']


# Needed later with JWT tokens
# class LogoutSerializer(serializers.Serializer):
#     refresh_token = serializers.CharField()


# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
