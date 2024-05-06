from rest_framework import filters, generics

from .models import Establishment
from .permissions import IsPartnerOrReadOnly
from .serializers import EstablishmentSerializer

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
