from django.urls import path

from .views import (
    EstablishmentBannerDetailView,
    EstablishmentDetailView,
    EstablishmentListCreateView,
)

urlpatterns = [
    path('', EstablishmentListCreateView.as_view(), name='establishment-list'),
    path('<int:pk>/', EstablishmentDetailView.as_view(), name='establishment-detail'),
    path('banners/<int:pk>', EstablishmentBannerDetailView.as_view(), name='banner-detail'),
]
