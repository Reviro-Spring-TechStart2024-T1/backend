from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ChangePasswordView,
    LogoutView,
    PartnerListCreateView,
    UserProfileView,
    UserRegisterView,
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('register/partner/', PartnerListCreateView.as_view(), name='register_partner'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
