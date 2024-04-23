from django.urls import path
from .views import EstablishmentListCreateView, EstablishmentDetailView

urlpatterns = [
    path('', EstablishmentListCreateView.as_view(), name='establishment-list'),
    path('<int:pk>/', EstablishmentDetailView.as_view(), name='establishment-detail'),
]
