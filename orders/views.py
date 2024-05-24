from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
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
            'user'
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
    queryset = Order.objects.all()
    permission_classes = [IsPartnerOnly]

    def get_queryset(self):
        partner = self.request.user
        qs = Order.objects.filter(
            menu__establishment__owner=partner
        ).select_related('beverage')
        return qs

    def get_orders_by_day(self, start_date, end_date):
        orders_by_day = {}
        current_day = start_date

        while current_day <= end_date:
            orders = self.get_queryset().filter(order_date__date=current_day)
            orders_total_count = orders.count()
            orders_total_sum = orders.aggregate(total_sum=Sum('beverage__price'))['total_sum'] or 0
            orders_by_day[current_day.strftime('%Y-%m-%d')] = {
                'count': orders_total_count,
                'sum': orders_total_sum
            }
            current_day += timedelta(days=1)

        return orders_by_day

    def get_orders_by_week(self, start_date, end_date):
        orders_by_week = {}
        current_week_start = start_date

        while current_week_start <= end_date:
            current_week_end = current_week_start + timedelta(days=6)
            if current_week_end > end_date:
                current_week_end = end_date
            week_orders = self.get_queryset().filter(order_date__date__range=[current_week_start, current_week_end])
            week_orders_count = week_orders.count()
            week_orders_sum = week_orders.aggregate(total_sum=Sum('beverage__price'))['total_sum'] or 0
            orders_by_week[
                (str(current_week_start.strftime('%Y-%m-%d')) + ' - ' +  # noqa: W504
                 str(current_week_end.strftime('%Y-%m-%d')))
            ] = {
                'count': week_orders_count,
                'sum': week_orders_sum
            }

            current_week_start += timedelta(days=7)

        return orders_by_week

    def get_orders_by_month(self, start_date, end_date):
        orders_by_month = {}
        current_month_start = start_date

        while current_month_start <= end_date:
            current_month_end = current_month_start + relativedelta(months=1, days=-1)
            if current_month_end > end_date:
                current_month_end = end_date
            month_data = self.get_orders_by_week(current_month_start, current_month_end)
            month_count = sum(week_data['count'] for week_data in month_data.values())
            month_sum = sum(week_data['sum'] for week_data in month_data.values())
            orders_by_month[current_month_start.strftime('%Y-%m')] = {
                'count': month_count,
                'sum': month_sum
            }
            current_month_start += relativedelta(months=1)

        return orders_by_month

    def get_orders_by_quarter(self, start_date, end_date):
        orders_by_quarter = {}
        current_quarter_start = self.get_start_of_quarter(start_date)

        while current_quarter_start <= end_date:
            current_quarter_end = current_quarter_start + relativedelta(months=3, days=-1)
            if current_quarter_end > end_date:
                current_quarter_end = end_date
            quarter_data = self.get_orders_by_month(current_quarter_start, current_quarter_end)
            quarter_count = sum(month_data['count'] for month_data in quarter_data.values())
            quarter_sum = sum(month_data['sum'] for month_data in quarter_data.values())
            quarter_label = f'Q{(current_quarter_start.month - 1) // 3 + 1}_{current_quarter_start.year}'
            orders_by_quarter[quarter_label] = {
                'count': quarter_count,
                'sum': quarter_sum
            }
            current_quarter_start += relativedelta(months=3)

        return orders_by_quarter

    def get_start_of_quarter(self, date):
        quarter_month = (date.month - 1) // 3 * 3 + 1
        return datetime(date.year, quarter_month, 1, tzinfo=date.tzinfo)

    def get_end_of_quarter(self, date):
        # Calculate the start month of the next quarter
        next_quarter_month = (date.month - 1) // 3 * 3 + 1 + 3

        # If next quarter's month is greater than 12, set it to 12
        if next_quarter_month > 12:
            next_quarter_month = 12

        # Calculate the last day of the quarter
        last_day_of_quarter = (datetime(date.year, next_quarter_month, 1) - timedelta(days=1)).day

        # Return the end of the quarter
        return datetime(date.year, next_quarter_month - 1, last_day_of_quarter, tzinfo=date.tzinfo)

    def get_start_of_week(self, date):
        # Calculate the start of the week (Monday)
        start_of_week = date - timedelta(days=date.weekday())
        return start_of_week

    def get_start_of_month(self, date):
        # Calculate the start of the month
        start_of_month = date.replace(day=1)
        return start_of_month

    def get_start_of_year(self, date):
        return datetime(date.year, 1, 1, tzinfo=date.tzinfo)

    def get_end_of_year(self, date):
        return datetime(date.year, 12, 31, 23, 59, 59, tzinfo=date.tzinfo)

    def get(self, request, *args, **kwargs):
        today = timezone.now()
        this_week_start = self.get_start_of_week(today)
        last_week_end = this_week_start - timedelta(days=1)
        last_week_start = last_week_end - timedelta(days=6)

        this_month_start = self.get_start_of_month(today)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = self.get_start_of_month(last_month_end)

        this_quarter_start = self.get_start_of_quarter(today)
        last_quarter_start = self.get_start_of_quarter(this_quarter_start - timedelta(days=60))
        last_quarter_end = self.get_end_of_quarter(this_quarter_start - timedelta(days=30))

        this_year_start = self.get_start_of_year(today)
        last_year_start = self.get_start_of_year(today - timedelta(days=360))
        last_year_end = self.get_end_of_year(today - timedelta(days=360))

        response_data = {
            'this_week': self.get_orders_by_day(this_week_start, today),
            'last_week': self.get_orders_by_day(last_week_start, last_week_end),
            'this_month': self.get_orders_by_week(this_month_start, today),
            'last_month': self.get_orders_by_week(last_month_start, last_month_end),
            'this_quarter': self.get_orders_by_month(this_quarter_start, today),
            'last_quarter': self.get_orders_by_month(last_quarter_start, last_quarter_end),
            'this_year': self.get_orders_by_quarter(this_year_start, today),
            'last_year': self.get_orders_by_quarter(last_year_start, last_year_end),
        }

        return Response(response_data)
