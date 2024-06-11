from django.urls import path

from .views import (
    EstablishmentBannerCreateView,
    EstablishmentBannerDeleteView,
    EstablishmentDetailView,
    EstablishmentListCreateView,
    EstablishmentMapListView,
    PartnerEstablishmentListView,
)

urlpatterns = [
    path('', EstablishmentListCreateView.as_view(), name='establishment-list'),
    path('<int:pk>/', EstablishmentDetailView.as_view(), name='establishment-detail'),
    path('banners/', EstablishmentBannerCreateView.as_view(), name='banner-create'),
    path('banners/<int:pk>/', EstablishmentBannerDeleteView.as_view(), name='banner-delete'),
    path('partner/', PartnerEstablishmentListView.as_view(), name='partner-establishment-list'),
    path('all/', EstablishmentMapListView.as_view(), name='establishments-all'),
]
