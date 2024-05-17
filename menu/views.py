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
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsPartnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        beverage_name = self.request.query_params.get('beverage_name', None)
        if beverage_name:
            queryset = queryset.filter(
                beverages__name__icontains=beverage_name
            ).distinct()
        return queryset


class MenuDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsPartnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        beverage_name = self.request.query_params.get('beverage_name', None)
        if beverage_name:
            queryset = queryset.filter(
                beverages__name__icontains=beverage_name
            ).distinct()
        return queryset


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
