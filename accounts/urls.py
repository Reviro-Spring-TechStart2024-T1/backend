from django.urls import path
from .views import UserRegisterView, UserProfileView, ChangePasswordView

urlpatterns = [
    path('api/register/', UserRegisterView.as_view(), name='register'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
