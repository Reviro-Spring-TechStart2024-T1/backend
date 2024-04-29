from django.urls import path

from .views import (
    BeverageDetailView,
    BeverageListCreateView,
    CategoryDetailView,
    CategoryListCreateView,
    MenuDetailView,
    MenuListCreateView,
    QrCodeCreate,
    QrCodeDelete,
    QrCodeDetail,
    QrCodeList,
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('menus/', MenuListCreateView.as_view(), name='menu-list'),
    path('menus/<int:pk>/', MenuDetailView.as_view(), name='menu-detail'),
    path('beverages/', BeverageListCreateView.as_view(), name='beverage-list'),
    path('beverages/<int:pk>/', BeverageDetailView.as_view(), name='beverage-detail'),
    path('qrcodes/', QrCodeList.as_view(), name='qrcode-list'),
    path('qrcodes/<int:pk>/', QrCodeDetail.as_view(), name='qrcode-detail'),
    path('qrcodes/create/<int:menu_id>/', QrCodeCreate.as_view(), name='create-qrcode'),
    path('qrcodes/delete/<int:pk>/', QrCodeDelete.as_view(), name='delete-qrcode'),
]
