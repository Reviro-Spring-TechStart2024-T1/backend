from django.urls import path

from .views import EstablishmentDetailView, EstablishmentListCreateView

urlpatterns = [
    path('', EstablishmentListCreateView.as_view(), name='establishment-list'),
    path('<int:pk>/', EstablishmentDetailView.as_view(), name='establishment-detail'),
]
