from django.urls import path

from .views import (
    ItemCategoryDetailView,
    ItemCategoryListCreateView,
    MenuDetailView,
    MenuItemDetailView,
    MenuItemListCreateView,
    QrCodeCreateView,
    QrCodeDetailView,
)

urlpatterns = [
    path('item-categories/', ItemCategoryListCreateView.as_view(), name='item-category-list'),
    path('item-categories/<int:pk>/', ItemCategoryDetailView.as_view(), name='item-category-detail'),
    path('menus/<int:pk>/', MenuDetailView.as_view(), name='menu-detail'),
    path('menu-items/', MenuItemListCreateView.as_view(), name='menu-item-list'),
    path('menu-items/<int:pk>/', MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('qrcodes/<int:pk>/', QrCodeDetailView.as_view(), name='qrcode-detail'),
    path('qrcodes/create/', QrCodeCreateView.as_view(), name='qrcode-create')
]
