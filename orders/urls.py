from django.urls import path

from .views import (
    PartnersOrderCreateView,
    PartnersOrderDetailView,
    PartnersOrderListView,
    UsersOrderListCreateView,
)

urlpatterns = [
    path('partners/', PartnersOrderListView.as_view(), name='partners-order-list'),
    path('partners/create/', PartnersOrderCreateView.as_view(), name='partners-order-create'),
    path('partners/<int:pk>/', PartnersOrderDetailView.as_view(), name='partners-order-detail'),
    path('users/', UsersOrderListCreateView.as_view(), name='users-order-list-create'),
]
