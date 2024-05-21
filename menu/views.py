from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics

from establishments.permissions import IsPartnerOrReadOnly

from .models import Beverage, Category, Menu
from .permissions import IsAdminOrReadOnly
from .serializers import BeverageSerializer, CategorySerializer, MenuSerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class MenuListCreateView(generics.ListCreateAPIView):
    queryset = Menu.objects.filter(establishment__is_active=True)
    serializer_class = MenuSerializer
    permission_classes = [IsPartnerOrReadOnly]

    @extend_schema(
        summary='Get menus',
        description=(
            'Retrieves menus that belong to a partner.'
            ' Although anyone can access this page,'
            ' it is necessary only for frontend to see the list of menus,'
            ' mobile department does not need to use it.\n'
            '- Requires authentication.\n'
            '- Permission: Authenticated only.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Create menu',
        description=(
            'Creates menu, necessary to pass establishments id.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        '''
        Get the authenticated partner
        Filter the queryset to get all menus owned by partner
        '''

        partner = self.request.user

        queryset = Menu.objects.filter(establishment__owner=partner)

        return queryset


class MenuDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.filter(establishment__is_active=True)
    serializer_class = MenuSerializer
    permission_classes = [IsPartnerOrReadOnly]

    @extend_schema(
        summary='Get menu',
        description=(
            'Retrieves specific menu.\n'
            '- Requires authentication.\n'
            '- Permission: Authenticated only.'
        ),
        parameters=[
            OpenApiParameter(
                name='beverage__name',
                description='Case-insensitive filter that gets beverages matching specified string.',
                required=False,
                type=str
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Update menu',
        description=(
            'Update sepcific menu\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update menu',
        description=(
            'Partially update sepcific menu.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary='Delete menu',
        description=(
            'Delete sepcific menu.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.'
        )
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class BeverageListCreateView(generics.ListCreateAPIView):
    queryset = Beverage.objects.all()
    serializer_class = BeverageSerializer
    permission_classes = [IsPartnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'price', 'category__name']


class BeverageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Beverage.objects.all()
    serializer_class = BeverageSerializer
    permission_classes = [IsPartnerOrReadOnly]
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['name', 'price']
