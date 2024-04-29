from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from establishments.permissions import IsPartnerOrReadOnly

from .models import Beverage, Category, Menu, QrCode
from .permissions import IsAdminOrReadOnly, IsAdminUser
from .serializers import (
    BeverageSerializer,
    CategorySerializer,
    MenuSerializer,
    QrCodeSerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
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


class QrCodeList(generics.ListAPIView):
    queryset = QrCode.objects.all()
    serializer_class = QrCodeSerializer
    permission_classes = [IsAdminOrReadOnly]


class QrCodeDetail(generics.RetrieveAPIView):
    queryset = QrCode.objects.all()
    serializer_class = QrCodeSerializer
    permission_classes = [IsAdminOrReadOnly]


class QrCodeCreate(generics.CreateAPIView):
    queryset = QrCode.objects.all()
    serializer_class = QrCodeSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        menu_id = self.kwargs.get('menu_id')
        menu = get_object_or_404(Menu, pk=menu_id)

        # Ensure no duplicate QR code exists
        if QrCode.objects.filter(menu=menu).exists():
            raise ValidationError({'detail': 'A QR Code for this establishment already exists.'})

        serializer.save(menu=menu)


class QrCodeDelete(generics.DestroyAPIView):
    queryset = QrCode.objects.all()
    serializer_class = QrCodeSerializer
    permission_classes = [IsAdminUser]
