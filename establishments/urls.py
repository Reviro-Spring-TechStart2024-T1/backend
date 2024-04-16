from django.urls import path
from .views import EstablishmentListCreateView, EstablishmentDetailView

urlpatterns = [
    path('establishments/', EstablishmentListCreateView.as_view(), name='establishment-list'),
    path('establishments/<int:pk>/', EstablishmentDetailView.as_view(), name='establishment-detail'),
]
