from rest_framework import generics

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


class MenuDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsPartnerOrReadOnly]


class BeverageListCreateView(generics.ListCreateAPIView):
    queryset = Beverage.objects.all()
    serializer_class = BeverageSerializer
    permission_classes = [IsPartnerOrReadOnly]


class BeverageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Beverage.objects.all()
    serializer_class = BeverageSerializer
    permission_classes = [IsPartnerOrReadOnly]
