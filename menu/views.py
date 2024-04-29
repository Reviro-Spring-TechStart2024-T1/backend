from rest_framework import generics

from establishments.permissions import IsPartnerOrReadOnly

from .models import ItemCategory, Menu, MenuItem
from .permissions import IsAdminOrReadOnly
from .serializers import (
    ItemCategorySerializer,
    MenuItemSerializer,
    MenuSerializer,
    MenuSpecificSerializer,
)


class ItemCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ItemCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class MenuDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()  # select_related('items')
    serializer_class = MenuSpecificSerializer
    permission_classes = [IsPartnerOrReadOnly]


class MenuCreateView(generics.CreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsPartnerOrReadOnly]


class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsPartnerOrReadOnly]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsPartnerOrReadOnly]
