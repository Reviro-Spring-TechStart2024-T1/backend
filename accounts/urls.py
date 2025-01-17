from django.urls import include, path

from .views import (
    BlockPartnerView,
    ChangePasswordView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    PartnerListCreateView,
    UnblockPartnerView,
    UserListView,
    UserProfileView,
    UserRegisterView,
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('register/partner/', PartnerListCreateView.as_view(), name='register_partner'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('', UserListView.as_view(), name='users_list'),
    path('partner/block/', BlockPartnerView.as_view(), name='block-partner'),
    path('partner/unblock/', UnblockPartnerView.as_view(), name='unblock-partner'),
]
