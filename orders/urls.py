from django.urls import path

from .views import PartnersOrderDetailView, PartnersOrderListView, UsersOrderListView

urlpatterns = [
    path('partners/', PartnersOrderListView.as_view(), name='partners-order-list'),
    path('partners/<int:pk>/', PartnersOrderDetailView.as_view(), name='partners-order-detail'),
    path('', UsersOrderListView.as_view(), name='users-order-list')
]
