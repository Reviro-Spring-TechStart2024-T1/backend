from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
    ):

        if not email:
            raise ValueError('The email address must be set')

        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None):
        user = self.create_user(
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.role = 'admin'
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    USER_ROLES = [
        ('customer', 'Customer'),
        ('partner', 'Establishment Partner'),
        ('admin', 'Administrator'),
    ]

    SEX_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('not_say', 'Prefer not to say')
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', null=True, blank=True)
    role = models.CharField(max_length=25, choices=USER_ROLES, default='customer')
    sex = models.CharField(max_length=18, choices=SEX_CHOICES, default='not_say')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def tokens(self):
        access = AccessToken.for_user(self)
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(access)
        }
