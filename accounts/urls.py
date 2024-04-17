from django.urls import path
from .views import UserRegisterView, UserProfileView, ChangePasswordView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
