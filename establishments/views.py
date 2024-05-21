from rest_framework import filters, generics

from .models import Establishment, EstablishmentBanner
from .permissions import IsPartnerOrReadOnly
from .serializers import EstablishmentBannerSerializer, EstablishmentSerializer

# from django_filters.rest_framework import DjangoFilterBackend


class EstablishmentListCreateView(generics.ListCreateAPIView):
    queryset = Establishment.objects.filter(is_active=True)
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EstablishmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Establishment.objects.filter(is_active=True)
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
