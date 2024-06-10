from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CaputeOrderViewV2PayPalAPI,
    CreateOrderViewV2PayPalAPI,
    CreatePaymentView,
    CreateProductView,
    ExecutePaymentView,
    PayPalCreatePlanView,
    ProductsListView,
    ProductView,
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
    path('create-order', CreateOrderViewV2PayPalAPI.as_view(), name='create-order'),
    path('capture-order', CaputeOrderViewV2PayPalAPI.as_view(), name='capture-order'),
    path('create-product', CreateProductView.as_view(), name='create-product'),
    path('products', ProductsListView.as_view(), name='subs-products'),
    path('products/<int:pk>', ProductView.as_view(), name='subs-products'),
    path('plan', PayPalCreatePlanView.as_view(), name='paypal_subs'),
]
