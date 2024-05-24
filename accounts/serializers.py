import re

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User
from .utils import generate_strong_password


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

        tokens = user.tokens()

        return tokens


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


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for the logout endpoint.

    This serializer expects a JSON object with a single key:
        - refresh_token: A string representing the refresh token to be invalidated.

    Upon successful execution, this serializer invalidates the provided refresh token
    and does not return any data. If the refresh token is successfully invalidated,
    the user will be logged out of the system.
    """

    refresh_token = serializers.CharField()

    def validate(self, attrs):
        """
        Validates the input data.

        Args:
            attrs (dict): The input data containing the refresh token.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the refresh token is missing.
        """

        refresh_token = attrs['refresh_token']

        if not refresh_token:
            raise serializers.ValidationError({'detail': 'Refresh token is required.'}, 400)

        return attrs

    def save(self, **kwargs):
        """
        Invalidates the provided refresh token.

        Args:
            **kwargs: Additional keyword arguments.

        Raises:
            serializers.ValidationError: If the refresh token is invalid.
        """

        refresh_token = self.validated_data['refresh_token']

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            raise serializers.ValidationError({'detail': 'Invalid refresh token.'}, 400)


class PartnerUserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'role',
            'date_of_birth',
            'email',
            'sex',
            'is_blocked',
        ]
        read_only_fields = [
            'id',
            'first_name',
            'last_name',
            'role',
            'date_of_birth',
            'sex',
            'is_blocked',
        ]

    def create(self, validated_data):

        random_password = generate_strong_password()

        user = User.objects.create_user(
            email=validated_data['email'],
            password=random_password
        )

        user.role = 'partner'
        user.save()

        # Send email to the created user
        login_url = settings.ALLOWED_HOSTS[0] + reverse('token_obtain_pair')
        subject = 'Your DrinkJoy Account Information'
        message = (f'Your account with the role \'partner\' has been created.\n\n'
                   f'Email: {validated_data["email"]}\n'
                   f'Password: {random_password}\n\n'
                   f'Please make sure to update your password after first login.\n'
                   f'Login URL: https://{login_url}\n\n'
                   f'Best regards,\n'
                   f'Your DrinkJoy Team\n\n'
                   f'If you received this email by mistake please ignore it.')
        from_email = settings.EMAIL_HOST_USER
        to_email = [validated_data['email']]
        send_mail(subject, message, from_email, to_email, fail_silently=False)

        return user


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['role'] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Check if the user is blocked
        if user.is_blocked:
            raise PermissionDenied(detail='Your account is blocked, please '
                                   'refer to the administrator for further assistance.')

        data['role'] = user.role
        return data


class PartnerBlockUnblockSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'is_blocked',
            'date_of_birth',
            'avatar',
            'role',
            'sex',
        ]
        read_only_fields = [
            'id',
            'first_name',
            'last_name',
            'is_blocked',
            'date_of_birth',
            'avatar',
            'role',
            'sex',
        ]
