from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from .models import Order
from .permissions import IsCustomerOnly, IsPartnerOnly
from .serializers import PartnersOrderSerializer, UsersOrderSerializer


class PartnersOrderListView(generics.ListAPIView):
    '''
    List of all orders available for a partner to see
    '''
    queryset = Order.objects.all()
    serializer_class = PartnersOrderSerializer
    permission_classes = [IsPartnerOnly]

    @swagger_auto_schema(
        operation_summary='Get partners\' orders list',
        operation_description='''
        Retrieve a list of orders for all the establishments of partner.
        - Requires authentication.
        - Permission: Partners only.
        '''
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        '''
        Get the authenticated partner
        Filter the queryset to get all beverages ordered by establishments owned by the partner
        '''

        partner = self.request.user

        queryset = Order.objects.filter(beverage__menu__establishment__owner=partner)

        return queryset


class PartnersOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = PartnersOrderSerializer
    permission_classes = [IsPartnerOnly]

    @swagger_auto_schema(
        operation_summary='Get order',
        operation_description='''
        Retrieve an order by its id.
        - Requires authentication.
        - Permission: Partners only.
        '''
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update order',
        operation_description='''
        Partner can update only status of the order.
        - Requires authentication.
        - Permission: Partners only.
        '''
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partially update order',
        operation_description='''
        Partner can partially update only status of the order.
        - Requires authentication.
        - Permission: Partners only.
        '''
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_queryset(self):
        '''
        Get the authenticated partner
        Filter the queryset to get all beverages ordered by establishments owned by the partner
        '''

        partner = self.request.user

        queryset = Order.objects.filter(beverage__menu__establishment__owner=partner)

        return queryset


class UsersOrderListView(generics.ListCreateAPIView):
    '''
    Allows customer users to view a list of their orders and create new orders.

    GET:
    - Requires authentication.
    - Only accessible to users with the customer role.
    - Returns a list of orders created by the authenticated customer user.

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
        operation_summary='Get customers\' orders list',
        operation_description='''
        Retrieve a list of orders created by the authenticated customer user.
        - Requires authentication.
        - Each customer gets only their own list of made orders.
        - Permission: Customers only.
        '''
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create order',
        operation_description='''
        Create a new order for the authenticated customer user.
        - Requires authentication.
        - To create new order pass beverages id to the field "beverage_id".
        - Returns the newly created order.
        - Permission: Customers only.
        '''
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        '''
        Get the authenticated user
        Filter the queryset to show only the orders belonging to the authenticated user
        '''

        queryset = Order.objects.filter(user=self.request.user)

        return queryset
