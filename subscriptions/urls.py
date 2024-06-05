from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CreateOrderViewV2PayPAlAPI,
    CreatePaymentView,
    ExecutePaymentView,
    SubscriptionPlanViewSet,
    UserSubscriptionViewSet,
)

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'users', UserSubscriptionViewSet, basename='user-subscription')


urlpatterns = [
    path('', include(router.urls)),
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('execute-payment/', ExecutePaymentView.as_view(), name='execute-payment'),
    path('create-order', CreateOrderViewV2PayPAlAPI.as_view(), name='create-order'),
]
