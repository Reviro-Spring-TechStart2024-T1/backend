import os

import geocoder
from dotenv import load_dotenv
from rest_framework import filters, generics

from .models import Establishment, EstablishmentBanner
from .permissions import IsPartnerOrReadOnly
from .serializers import EstablishmentBannerSerializer, EstablishmentSerializer

# from django_filters.rest_framework import DjangoFilterBackend

load_dotenv()


class EstablishmentListCreateView(generics.ListCreateAPIView):
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        address = serializer.initial_data['address']
        g = geocoder.google(address, key=os.environ.get('GOOGLE_MAPS_KEY'))
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        point = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'
        serializer.save(
            owner=self.request.user,
            location=point
        )

    def get_queryset(self):
        partner = self.request.user
        return super().get_queryset().filter(owner=partner)

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)

    #     address = serializer.validated_data.get('address', instance.address)
    #     g = geocoder.google(address, key=os.environ.get('GOOGLE_MAPS_KEY'))
    #     latitude = g.latlng[0]
    #     longitude = g.latlng[1]
    #     point = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'

    #     serializer.save(
    #         location=point
    #     )

    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         instance._prefetched_objects_cache = {}

    #     return Response(serializer.data)

    # def preform_update(self, serializer):
    #     address = serializer.initial_data['address']
    #     g = geocoder.google(address, key=os.environ.get('GOOGLE_MAPS_KEY'))
    #     latitude = g.latlng[0]
    #     longitude = g.latlng[1]
    #     point = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'
    #     serializer.save(
    #         owner=self.request.user,
    #         location=point
    #     )


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
