from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from .models import Establishment, EstablishmentBanner
from .permissions import IsPartnerOrReadOnly
from .serializers import (
    EstablishmentBannerSerializer,
    EstablishmentMapSerializer,
    EstablishmentSerializer,
)

# from django_filters.rest_framework import DjangoFilterBackend


class EstablishmentListCreateView(generics.ListCreateAPIView):
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EstablishmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]


class EstablishmentBannerCreateView(generics.CreateAPIView):
    queryset = EstablishmentBanner.objects.all()
    serializer_class = EstablishmentBannerSerializer
    permission_classes = [IsPartnerOrReadOnly]


class EstablishmentBannerDeleteView(generics.DestroyAPIView):
    queryset = EstablishmentBanner.objects.all()
    serializer_class = EstablishmentBannerSerializer
    permission_classes = [IsPartnerOrReadOnly]


class EstablishmentMapListView(generics.ListAPIView):
    '''
    This endpoint for customers to see all the existing establishments in maps
    '''
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentMapSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]


class PartnerEstablishmentListView(generics.ListAPIView):
    '''
    This view for partners to see their list of establishments
    '''
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]
    queryset = Establishment.objects.none()

    def get_queryset(self):
        return Establishment.objects.filter(owner=self.request.user)
