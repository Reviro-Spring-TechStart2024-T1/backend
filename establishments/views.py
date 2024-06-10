import logging

from rest_framework import filters, generics

from .models import Establishment, EstablishmentBanner
from .permissions import IsPartnerOrReadOnly
from .serializers import EstablishmentBannerSerializer, EstablishmentSerializer

# from django_filters.rest_framework import DjangoFilterBackend


logger = logging.getLogger(__name__)


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


class PartnerEstablishmentListView(generics.ListAPIView):
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]

    def get_queryset(self):
        return Establishment.objects.filter(owner=self.request.user)
