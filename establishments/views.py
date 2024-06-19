from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from .models import Establishment, EstablishmentBanner
from .permissions import IsPartnerOrReadOnly
from .serializers import (
    EstablishmentBannerSerializer,
    EstablishmentMapSerializer,
    EstablishmentSerializer,
)


class EstablishmentListCreateView(generics.ListCreateAPIView):
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary='Get establishments',
        description=(
            'Allows to authenticated users get list of paginated establishments.\n'
            '- Requires authentication.\n'
            '- Permission: Allowed to anyone.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Create establishment',
        description=(
            'Allows partner to create establishment.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EstablishmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]

    @extend_schema(
        summary='Get establishment',
        description=(
            'Allows to authenticated users get establishment.\n'
            '- Requires authentication.\n'
            '- Permission: Allowed to anyone.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Update establishment',
        description=(
            'Allows partner to update establishment.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update establishment',
        description=(
            'Allows partner to partially update establishment.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary='Delete establishment',
        description=(
            'Allows partner to delete establishment.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EstablishmentBannerCreateView(generics.CreateAPIView):
    queryset = EstablishmentBanner.objects.all()
    serializer_class = EstablishmentBannerSerializer
    permission_classes = [IsPartnerOrReadOnly]

    @extend_schema(
        summary='Create establishments banner',
        description=(
            'Allows partner to upload establishments banner. '
            'Field `url` accepts image, and shows the url to it after processing it on server side.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EstablishmentBannerDeleteView(generics.DestroyAPIView):
    queryset = EstablishmentBanner.objects.all()
    serializer_class = EstablishmentBannerSerializer
    permission_classes = [IsPartnerOrReadOnly]

    @extend_schema(
        summary='Delete establishments banner',
        description=(
            'Allows partner to delete establishments banner.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EstablishmentMapListView(generics.ListAPIView):
    '''
    This endpoint for customers to see all the existing establishments in maps
    '''
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentMapSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Get establishments on map',
        description=(
            'Allows customers to see all the existing establishments in maps.\n'
            '- Requires authentication.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PartnerEstablishmentListView(generics.ListAPIView):
    '''
    This view for partners to see their list of establishments
    '''
    serializer_class = EstablishmentSerializer
    permission_classes = [IsPartnerOrReadOnly]
    queryset = Establishment.objects.none()

    def get_queryset(self):
        return Establishment.objects.filter(owner=self.request.user)

    @extend_schema(
        summary='Get partners establishments',
        description=(
            'Allows partners to see their list of establishments.\n'
            '- Requires authentication.'
            '- Permission: Partner only.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
