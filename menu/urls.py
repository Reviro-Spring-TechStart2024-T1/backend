from django.urls import path

from .views import (
    ItemCategoryDetailView,
    ItemCategoryListCreateView,
    MenuCreateView,
    MenuDetailView,
    MenuItemDetailView,
    MenuItemListCreateView,
)

urlpatterns = [
    path('item-categories/', ItemCategoryListCreateView.as_view(), name='item-category-list'),
    path('item-categories/<int:pk>/', ItemCategoryDetailView.as_view(), name='item-category-detail'),
    path('menus/', MenuCreateView.as_view(), name='menu'),
    path('menus/<int:pk>/', MenuDetailView.as_view(), name='menu-detail'),
    path('menu-items/', MenuItemListCreateView.as_view(), name='menu-item-list'),
    path('menu-items/<int:pk>/', MenuItemDetailView.as_view(), name='menu-item-detail'),
]
