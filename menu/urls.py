from django.urls import path

from .views import (
    BeverageDetailView,
    BeverageListCreateView,
    CategoryDetailView,
    CategoryListCreateView,
    MenuDetailView,
    MenuListCreateView,
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('menus/', MenuListCreateView.as_view(), name='menu-list'),
    path('menus/<int:pk>/', MenuDetailView.as_view(), name='menu-detail'),
    path('beverages/', BeverageListCreateView.as_view(), name='beverage-list'),
    path('beverages/<int:pk>/', BeverageDetailView.as_view(), name='beverage-detail'),
]
