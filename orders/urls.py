from django.urls import path

from .views import (
    CustomersOrderListCreateView,
    DetailedCustomerProfileView,
    FindCustomerByEmailView,
    PartnerCustomersListView,
    PartnersOrderCreateView,
    PartnersOrderDetailView,
    PartnersOrderListView,
)

urlpatterns = [
    path('partners/', PartnersOrderListView.as_view(), name='partners-order-list'),
    path('partners/create/', PartnersOrderCreateView.as_view(), name='partners-order-create'),
    path('partners/<int:pk>/', PartnersOrderDetailView.as_view(), name='partners-order-detail'),
    path('partner-customers/', PartnerCustomersListView.as_view(), name='partner-customers-list'),
    path('partner-customers/<int:id>/', DetailedCustomerProfileView.as_view(), name='detailed-customer-profile'),
    path('find-customer/', FindCustomerByEmailView.as_view(), name='find-customer'),
    path('customers/', CustomersOrderListCreateView.as_view(), name='customers-order-list-create'),
]
