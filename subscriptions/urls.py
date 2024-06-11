from django.urls import path  # include,

from .views import (  # CreatePaymentView,; ExecutePaymentView,; SubscriptionPlanViewSet,; UserSubscriptionViewSet,
    CaputeOrderViewV2PayPalAPI,
    CaputePayPalSubscriptionAPI,
    CreateOrderViewV2PayPalAPI,
    CreatePayPalSubscriptionAPI,
    CreateProductView,
    PayPalCreatePlanView,
    ProductsListView,
    ProductView,
)

# from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
# router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plan')
# router.register(r'users', UserSubscriptionViewSet, basename='user-subscription')


urlpatterns = [
    # path('', include(router.urls)),
    # path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    # path('execute-payment/', ExecutePaymentView.as_view(), name='execute-payment'),
    path('create-order', CreateOrderViewV2PayPalAPI.as_view(), name='create-order'),
    path('create-subscription', CreatePayPalSubscriptionAPI.as_view(), name='create-subscription'),
    path('capture-order', CaputeOrderViewV2PayPalAPI.as_view(), name='capture-order'),
    path('capture-subscription', CaputePayPalSubscriptionAPI.as_view(), name='capture-subscription'),
    path('create-product', CreateProductView.as_view(), name='create-product'),
    path('products', ProductsListView.as_view(), name='subs-products'),
    path('products/<int:pk>', ProductView.as_view(), name='subs-products'),
    path('plan', PayPalCreatePlanView.as_view(), name='paypal_subs'),
]
