from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, first_name=None, last_name=None, password=None, role='customer', sex='Prefer not to say'):
        if not email:
            raise ValueError('The email address must be set')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            role=role,
            sex=sex
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role='admin',
            sex='Prefer not to say'
        )
        user.is_staff = True
        user.is_superuser = True
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
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', null=True, blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='customer')
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='not_say')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
