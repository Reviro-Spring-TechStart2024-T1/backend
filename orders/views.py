from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Order
from .permissions import IsCustomerOnly, IsPartnerOnly
from .serializers import (
    PartnersCreateOrderSerializer,
    PartnersDetailOrderSerializer,
    UsersOrderSerializer,
)


class PartnersOrderListView(generics.ListAPIView):
    '''
    List of all orders available for a partner to see
    '''
    queryset = Order.objects.all()
    serializer_class = PartnersDetailOrderSerializer
    permission_classes = [IsPartnerOnly]

    @extend_schema(
        summary='Get partners\' orders list',
        description=(
            f'Retrieve a list of orders for all the establishments of partner.\n'
            f'- Requires authentication.\n'
            f'- Permission: Partners only.'
        )

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
    '''
    Retrieve and update orders by partners
    '''
    serializer_class = PartnersDetailOrderSerializer
    permission_classes = [IsPartnerOnly]

    @extend_schema(
        summary='Get order',
        description=(
            f'Retrieve an order by its id.\n'
            f'- Requires authentication.\n'
            f'- Permission: Partners only.\n'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Update order',
        description=(
            f'Partner can update only status of the order.\n'
            f'- Requires authentication.\n'
            f'- Permission: Partners only.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update order',
        description=(
            f'Partner can partially update only status of the order.\n'
            f'- Requires authentication.\n'
            f'- Permission: Partners only.'
        )
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


class PartnersOrderCreateView(generics.CreateAPIView):
    ''''
    Create orders for customers by partners
    '''
    queryset = Order.objects.all()
    serializer_class = PartnersCreateOrderSerializer
    permission_classes = [IsPartnerOnly]

    @extend_schema(
        summary='Partner create order',
        description=(
            'Create a new order for a customer by the partner user.\n'
            '- Requires authentication.\n'
            '- To create a new order, pass the beverage id and customer id.\n'
            '- Returns the newly created order.\n'
            '- Permission: Partners only.'
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersOrderListCreateView(generics.ListCreateAPIView):
    '''
    Allows customer users to view a list of their orders and create new orders.

    GET:
    - Requires authentication.
    - Only accessible to users with the customer role.
    - Returns a list of orders created by the authenticated customer user.

    POST:
    - Requires authentication.
    - Only accessible to users with the customer role.
    - Allows authenticated customer users to create a new order during happy hours.
    - Returns the newly created order or error message if constraints are violated.

    Permissions:
    - Users with the customer role have access to both GET and POST endpoints.
    - Other user roles do not have access to these endpoints.
    '''

    serializer_class = UsersOrderSerializer
    permission_classes = [IsCustomerOnly]

    @extend_schema(
        summary='Get customers\' orders list',
        description=(
            f'Retrieve a list of orders created by the authenticated customer user.\n'
            f'- Requires authentication.\n'
            f'- Each customer gets only their own list of made orders.\n'
            f'- Permission: Customers only.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Create order',
        description=(
            f'Create a new order for the authenticated customer user.\n'
            f'- Requires authentication.\n'
            f'- To create new order pass beverages id to the field "beverage_id".\n'
            f'- Returns the newly created order.\n'
            f'- Permission: Customers only.'
        )
    )
    def post(self, request, *args, **kwargs):
        '''
        Create a new order.
        '''
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                # Handles specific errors from serializer with messages
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        '''
        Get the authenticated user
        Filter the queryset to show only the orders belonging to the authenticated user
        '''
        customer = self.request.user
        queryset = Order.objects.filter(user=customer)
        return queryset
