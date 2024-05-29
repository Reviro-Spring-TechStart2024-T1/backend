from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CreatePaymentView,
    ExecutePaymentView,
    SubscriptionPlanViewSet,
    UserSubscriptionViewSet,
)

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'user-subscriptions', UserSubscriptionViewSet, basename='user-subscription')


urlpatterns = [
    path('', include(router.urls)),
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('execute-payment/', ExecutePaymentView.as_view(), name='execute-payment'),
]
