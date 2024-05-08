from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from establishments.permissions import IsPartnerOrReadOnly

from .models import Order
from .permissions import IsCustomerOnly
from .serializers import PartnersOrderSerializer, UsersOrderSerializer


class PartnersOrderListView(generics.ListAPIView):
    '''
    List of all orders available for a partner to see
    '''
    queryset = Order.objects.all()  # need to add innate filter to show only the establishments related orders or only the partner related orders
    # because there is establishment_name in these things the partner related filter will suffice
    serializer_class = PartnersOrderSerializer
    permission_classes = [IsPartnerOrReadOnly]


class PartnersOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = PartnersOrderSerializer
    permission_classes = [IsPartnerOrReadOnly]


class UsersOrderListView(generics.ListCreateAPIView):
    '''
    Allows customer users to view a list of their orders and create new orders.

    GET:
    - Requires authentication.
    - Only accessible to users with the customer role.
    - Returns a list of orders created by the authenticated customer user. (in progress)

    POST:
    - Requires authentication.
    - Only accessible to users with the customer role.
    - Allows authenticated customer users to create a new order.
    - Returns the newly created order.

    Permissions:
    - Users with the customer role have access to both GET and POST endpoints.
    - Other user roles do not have access to these endpoints.
    '''

    queryset = Order.objects.all()
    serializer_class = UsersOrderSerializer
    permission_classes = [IsCustomerOnly]

    @swagger_auto_schema(
        operation_summary='Retrieve a list of orders',
        operation_description='Retrieve a list of orders created by the authenticated customer user.'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a new order',
        operation_description='Create a new order for the authenticated customer user.'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
