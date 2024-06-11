from datetime import datetime, timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .filters import PartnersOrdersListCustomFilter, UsersOrderListCustomFilter
from .models import Order
from .permissions import IsCustomerOnly, IsPartnerOnly
from .serializers import (
    CustomerOrderSerializer,
    CustomerSerializer,
    DetailedCustomerProfileSerializer,
    FindCustomerByEmailSerializer,
    OrderStatisticsSerializer,
    PartnersCreateOrderSerializer,
    PartnersDetailOrderSerializer,
)


class PartnersOrderListView(generics.ListAPIView):
    '''
    List of all orders available for a partner to see
    '''
    queryset = Order.objects.all()
    serializer_class = PartnersDetailOrderSerializer
    permission_classes = [IsPartnerOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PartnersOrdersListCustomFilter

    @extend_schema(
        summary='Get partners\' orders list',
        description=(
            'Retrieve a list of orders for all the establishments of partner.\n'
            '- Requires authentication.\n'
            '- Permission: Partners only.'
        ),
        parameters=[
            OpenApiParameter(
                name='order_date',
                description='Filter orders by exact order date in YYYY-MM-DD format.',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='id',
                description='Filter orders by their unique identifier.',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='status',
                description=(
                    'Filter orders by their status\n'
                    '- `pending` - Pending\n'
                    '- `completed` - Completed\n'
                    '- `cancelled` - Cancelled\n'
                ),
                required=False,
                enum=['pending', 'completed', 'cancelled'],
                default='pending'
            ),
            OpenApiParameter(
                name='beverage__name',
                description='Filter orders by the name of the associated beverage.',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='time',
                description=(
                    'Filter orders by predefined time ranges. Possible values are:\n'
                    '- `today`: Orders made today\n'
                    '- `yesterday`: Orders made yesterday\n'
                    '- `this_month`: Orders made this month\n'
                    '- `last_month`: Orders made last month\n'
                    '- `last_6_months`: Orders made in the last 6 months\n'
                    '- `this_year`: Orders made this year\n'
                    '- `last_year`: Orders made last year'
                ),
                required=False,
                type=str
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        '''
        Get the authenticated partner
        Filter the queryset to get all beverages ordered by establishments owned by the partner
        '''

        partner = self.request.user
        queryset = Order.objects.filter(beverage__menu__establishment__owner=partner).select_related(
            'beverage',
            'menu',
            'menu__establishment',
            # 'user'
        ).order_by('-order_date')

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


class PartnerCustomersListView(generics.ListAPIView):
    '''
    Retrieve a list of customers who have made orders at the partner's establishments.
    Supports search by first name, last name, or email.
    '''
    serializer_class = CustomerSerializer
    permission_classes = [IsPartnerOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']

    def get_queryset(self):
        '''
        Filter orders to get those related to the establishments owned by the partner
        '''
        partner = self.request.user
        partner_orders = Order.objects.filter(beverage__menu__establishment__owner=partner)
        customer_ids = partner_orders.values_list('user', flat=True).distinct()
        queryset = User.objects.filter(id__in=customer_ids)
        return queryset


class DetailedCustomerProfileView(generics.RetrieveAPIView):
    '''
    Retrieve a detailed profile of a customer, including personal information and
    order history for the partner's establishments.
    '''
    serializer_class = DetailedCustomerProfileSerializer
    permission_classes = [IsPartnerOnly]
    lookup_field = 'id'
    queryset = User.objects.all()

    def get_queryset(self):
        return super().get_queryset()


class FindCustomerByEmailView(APIView):
    '''
    Find any existing customer by email address.
    '''
    serializer_class = FindCustomerByEmailSerializer
    permission_classes = [IsPartnerOnly]

    def post(self, request):
        serializer = FindCustomerByEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                customer = User.objects.get(email=email, role='customer')
                customer_serializer = CustomerSerializer(customer)
                return Response(customer_serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'message': 'Customer does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomersOrderListCreateView(generics.ListCreateAPIView):
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

    serializer_class = CustomerOrderSerializer
    permission_classes = [IsCustomerOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UsersOrderListCustomFilter

    @extend_schema(
        summary='Get customers\' orders list',
        description=(
            f'Retrieve a list of orders created by the authenticated customer user.\n'
            f'- Requires authentication.\n'
            f'- Each customer gets only their own list of made orders.\n'
            f'- Permission: Customers only.'
        ),
        parameters=[
            OpenApiParameter(
                name='time',
                description=(
                    'Filter orders by predefined time ranges. Possible values are:\n'
                    '- `today`: Orders made today\n'
                    '- `yesterday`: Orders made yesterday\n'
                    '- `this_month`: Orders made this month\n'
                    '- `last_month`: Orders made last month\n'
                    '- `last_6_months`: Orders made in the last 6 months\n'
                    '- `this_year`: Orders made this year\n'
                    '- `last_year`: Orders made last year'
                ),
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='status',
                description=(
                    'Filter orders by their status\n'
                    '- `pending` - Pending\n'
                    '- `completed` - Completed\n'
                    '- `cancelled` - Cancelled\n'
                ),
                required=False,
                enum=['pending', 'completed', 'cancelled'],
                default='pending'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Create order',
        description=(
            'Create a new order for the authenticated customer user.\n'
            '- Requires authentication.\n'
            '- To create new order pass beverages id to the field "beverage_id".\n'
            '- Returns the newly created order.\n'
            '- Permission: Customers only.'
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
        if getattr(self, 'swagger_fake_view', False):
            # Returning an empty queryset to avoid errors during schema generation
            return Order.objects.none()

        customer = self.request.user
        queryset = Order.objects.filter(user=customer).select_related(
            'beverage',
            'menu',
            'menu__establishment',
            'user'
        ).order_by('-order_date')
        return queryset


class OrderStatisticsView(generics.GenericAPIView):
    serializer_class = OrderStatisticsSerializer
    queryset = Order.objects.all()
    permission_classes = [IsPartnerOnly]

    def get_end_of_quarter(self, date):
        '''
        Calculate the start month of the next quarter
        If next quarter's month is greater than 12, set it to 12
        Calculate the last day of the quarter
        Return the end of the quarter
        '''

        next_quarter_month = (date.month - 1) // 3 * 3 + 1 + 3

        if next_quarter_month > 12:
            next_quarter_month = 12

        last_day_of_quarter = (datetime(date.year, next_quarter_month, 1) - timedelta(days=1)).day

        return datetime(date.year, next_quarter_month - 1, last_day_of_quarter, tzinfo=date.tzinfo)

    def get_start_of_week(self, date):
        # Calculate the start of the week (Monday)
        start_of_week = date - timedelta(days=date.weekday())
        return start_of_week

    def get_start_of_month(self, date):
        # Calculate the start of the month
        start_of_month = date.replace(day=1)
        start_of_week_including_month_start = start_of_month - timedelta(days=start_of_month.weekday())
        return start_of_week_including_month_start

    def get_start_of_year(self, date):
        return datetime(date.year, 1, 1, tzinfo=date.tzinfo)

    def get_end_of_year(self, date):
        return datetime(date.year, 12, 31, 23, 59, 59, tzinfo=date.tzinfo)

    @extend_schema(
        summary='Get partners stats',
        description=(
            'Returns all timeframes for statistics with counts of orders made in an all establishments'
            ' as well as beverage price sums. Filtering for the partner and its establishments\' orders are present.\n'
            '- Requires authentication.\n'
            '- Permission: Partner only.\n\n'
            'Predefined available time frames:\n'
            '- `this_week` and `last_week` - daily stats\n'
            '- `this_month` and `last_month` - weekly stats\n'
            '- `this_quarter` and `last_quarter` - monthly stats\n'
            '- `this_year` and `last_year` - quarterly stats'
        )
    )
    def get(self, request, *args, **kwargs):
        today = timezone.now()
        partner = self.request.user

        this_week_start = self.get_start_of_week(today)
        last_week_end = this_week_start - timedelta(days=1)
        last_week_start = last_week_end - timedelta(days=6)

        this_month_start = self.get_start_of_month(today)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = self.get_start_of_month(last_month_end)

        this_quarter_start = Order.statistics.get_start_of_quarter(today)
        last_quarter_start = Order.statistics.get_start_of_quarter(this_quarter_start - timedelta(days=60))
        last_quarter_end = self.get_end_of_quarter(this_quarter_start - timedelta(days=30))

        this_year_start = self.get_start_of_year(today)
        last_year_start = self.get_start_of_year(today - timedelta(days=360))
        last_year_end = self.get_end_of_year(today - timedelta(days=360))

        response_data = {
            'this_week': Order.statistics.get_stats_by_day(partner, this_week_start, today),
            'last_week': Order.statistics.get_stats_by_day(partner, last_week_start, last_week_end),
            'this_month': Order.statistics.get_stats_by_week(partner, this_month_start, today),
            'last_month': Order.statistics.get_stats_by_week(partner, last_month_start, last_month_end),
            'this_quarter': Order.statistics.get_stats_by_month(partner, this_quarter_start, today),
            'last_quarter': Order.statistics.get_stats_by_month(partner, last_quarter_start, last_quarter_end),
            'this_year': Order.statistics.get_stats_by_quarter(partner, this_year_start, today),
            'last_year': Order.statistics.get_stats_by_quarter(partner, last_year_start, last_year_end),
        }

        return Response(response_data)
