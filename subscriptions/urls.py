from django.urls import path

from .views import (
    CaputeOrderViewV2PayPalAPI,
    CaputePayPalSubscriptionAPI,
    CreateOrderViewV2PayPalAPI,
    CreatePayPalSubscriptionAPI,
    CreateProductView,
    DeletePayPalSubscriptionPlanView,
    PayPalCreatePlanView,
    PayPalInactivePlanView,
    PlanActivateDeactivateView,
    PlanPatchView,
    PlanUpdatePricingSchemeView,
    ProductsListView,
    ProductView,
    UserSubscriptionDetailView,
    UserSubscriptionView,
)

urlpatterns = [
    path('create-order/', CreateOrderViewV2PayPalAPI.as_view(), name='create-order'),
    path('create-subscription/', CreatePayPalSubscriptionAPI.as_view(), name='create-subscription'),
    path('capture-order/', CaputeOrderViewV2PayPalAPI.as_view(), name='capture-order'),
    path('capture-subscription/', CaputePayPalSubscriptionAPI.as_view(), name='capture-subscription'),
    path('captured/', UserSubscriptionView.as_view(), name='capured-subscriptions'),
    path('captured/detail/', UserSubscriptionDetailView.as_view(), name='capured-subscriptions-detail'),
    path('create-product/', CreateProductView.as_view(), name='create-product'),
    path('products/', ProductsListView.as_view(), name='subs-products'),
    path('products/<int:pk>/', ProductView.as_view(), name='subs-products'),
    path('plans/', PayPalCreatePlanView.as_view(), name='paypal-plans'),
    path('plans/inactives/', PayPalInactivePlanView.as_view(), name='paypal-plans-inactives'),
    path('plans/actions/', PlanActivateDeactivateView.as_view(), name='paypal-plans-actions'),
    path('plans/patch/', PlanPatchView.as_view(), name='paypal-plans-patch'),
    path('plans/update-pricing-scheme/', PlanUpdatePricingSchemeView.as_view(), name='paypal-plans-update-pricing-scheme'),
    path('plans/delete/<str:plan_id>/', DeletePayPalSubscriptionPlanView.as_view(), name='delete-subscription-plan'),
]
