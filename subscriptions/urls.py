from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubscriptionPlanViewSet, UserSubscriptionViewSet

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet)
router.register(r'subscriptions', UserSubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
