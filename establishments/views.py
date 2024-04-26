from rest_framework import generics

from .models import Establishment
from .permissions import IsPartnerOrReadOnly
from .serializers import EstablishmentSerializer


class EstablishmentListCreateView(generics.ListCreateAPIView):
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EstablishmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]
