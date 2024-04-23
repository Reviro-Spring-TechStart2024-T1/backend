from rest_framework import generics, permissions

from .models import ItemCategory, Menu, MenuItem, QrCode
from .permissions import IsAdminOrReadOnly
from .serializers import (
    ItemCategorySerializer,
    MenuItemSerializer,
    MenuSerializer,
    QrCodeSerializer,
)


class ItemCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ItemCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class MenuDetailView(generics.RetrieveUpdateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]


class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class QrCodeDetailView(generics.RetrieveUpdateAPIView):
    queryset = QrCode.objects.all()
    serializer_class = QrCodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class QrCodeCreateView(generics.CreateAPIView):
    queryset = QrCode.objects.all()
    serializer_class = QrCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
