from django.urls import path

from .views import (
    CustomersOrderListCreateView,
    DetailedCustomerProfileView,
    FindCustomerByEmailView,
    OrderStatisticsView,
    PartnerCustomersListView,
    PartnersOrderCreateView,
    PartnersOrderDetailView,
    PartnersOrderListView,
)

urlpatterns = [
    path('partners/', PartnersOrderListView.as_view(), name='partners-order-list'),
    path('partners/establishments/<int:establishment_id>/',
         PartnersOrderListView.as_view(), name='partners-order-list-by-establishment'),
    path('partners/create/', PartnersOrderCreateView.as_view(), name='partners-order-create'),
    path('partners/<int:pk>/', PartnersOrderDetailView.as_view(), name='partners-order-detail'),
    path('partner-customers/', PartnerCustomersListView.as_view(), name='partner-customers-list'),
    path('partners-customers/<int:establishment_id>/',
         PartnerCustomersListView.as_view(), name='partner-customers-list-by-establishment'),
    path('partner-customers/<int:id>/', DetailedCustomerProfileView.as_view(), name='detailed-customer-profile'),
    path('partners/stats/', OrderStatisticsView.as_view(), name='partner-stats'),
    path('partners/stats/<int:establishment_id>/', OrderStatisticsView.as_view(), name='partner-stats-by-establishment'),
    path('find-customer/', FindCustomerByEmailView.as_view(), name='find-customer'),
    path('customers/', CustomersOrderListCreateView.as_view(), name='customers-order-list-create'),
]
