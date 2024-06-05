import json

import requests
from django.shortcuts import get_object_or_404
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubscriptionPlan, UserSubscription
from .serializers import (
    CreatePaymentSerializer,
    SubscriptionPlanSerializer,
    UserSubscriptionCreateSerializer,
    UserSubscriptionSerializer,
)
from .utils import create_payment, execute_payment, paypal_token


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePaymentSerializer

    @extend_schema(
        summary='Create PayPal Payment',
        description=(
            'This view handles creating a PayPal payment.\n\n'
            'Flow:\n'
            '1. The user selects a subscription plan.\n'
            "2. A PayPal payment is created with the plan's price.\n"
            '3. The user is redirected to PayPal to approve the payment.'
        ),
        request=CreatePaymentSerializer,
    )
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            plan_id = serializer.validated_data['plan_id']
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
            except SubscriptionPlan.DoesNotExist:
                return Response({'error': 'Invalid plan_id'}, status=status.HTTP_400_BAD_REQUEST)

        amount = plan.price
        return_url = request.build_absolute_uri(reverse('execute-payment'))
        cancel_url = request.build_absolute_uri(reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))
        print('execute:', reverse('execute-payment'))
        print('cancel:', reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))
        payment = create_payment(amount, return_url, cancel_url)
        if payment:
            for link in payment['links']:
                if link['rel'] == 'approval_url':
                    approval_url = link['href']
                    return Response({'approval_url': approval_url}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Payment creation failed'}, status=status.HTTP_400_BAD_REQUEST)


class ExecutePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Execute PayPal Payment',
        description=(
            'This view handles executing the PayPal payment.\n\n'
            'Flow:\n'
            '1. After the user approves the payment on PayPal, they are redirected back to this view.\n'
            '2. The payment details are verified.\n'
            '3. A new subscription is created and associated with the user.'
        ),
        parameters=[
            OpenApiParameter(
                name='paymentId',
                type=str,
                location=OpenApiParameter.QUERY,
                description='ID of the PayPal payment.'
            ),
            OpenApiParameter(
                name='PayerID',
                type=str,
                location=OpenApiParameter.QUERY,
                description='ID of the PayPal payer.'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=UserSubscriptionSerializer,
                description='Payment executed successfully and subscription created.'
            ),
            400: OpenApiResponse(description='Payment execution failed'),
            500: OpenApiResponse(description='Internal server error'),
        },
    )
    def get(self, request):
        payment_id = request.query_params.get('paymentId')
        payer_id = request.query_params.get('PayerID')
        payment = execute_payment(payment_id, payer_id)
        if payment:
            try:
                transaction = payment['transactions'][0]
                plan_id = transaction['item_list']['items'][0]['sku']
                plan = get_object_or_404(SubscriptionPlan, id=plan_id)

                subscription = UserSubscription.objects.create(
                    user=request.user,
                    plan=plan,
                    is_trial=False,
                )
                subscription.save()
                return Response({'status': 'Payment executed successfully'}, status=status.HTTP_200_OK)
            except (KeyError, IndexError, SubscriptionPlan.DoesNotExist) as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Payment execution failed'}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API for viewing subscription plans.
    '''
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    CRUD operations of the user subscriptions.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Customers can only view their active subscriptions
        return UserSubscription.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSubscriptionCreateSerializer
        return UserSubscriptionSerializer

    def perform_destroy(self, instance):
        # Destroy method to deactivate instead of deleting
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        subscription = self.get_object()
        additional_days = request.data.get(
            'additional_days', subscription.plan.duration.days)  # Allow variable extension
        subscription.extend_subscription(additional_days)
        resp_data = {'status': 'subscription extended', 'end_date': subscription.end_date}
        return Response(resp_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.cancel_subscription()
        resp_data = {'status': 'subscription canceled'}
        return Response(resp_data, status=status.HTTP_200_OK)


class CreateOrderViewV2PayPAlAPI(APIView):
    serializer_class = CreatePaymentSerializer

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            plan_id = serializer.validated_data['plan_id']
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
            except SubscriptionPlan.DoesNotExist:
                return Response({'error': 'Invalid plan_id'}, status=status.HTTP_400_BAD_REQUEST)

        return_url = request.build_absolute_uri(reverse('execute-payment'))
        cancel_url = request.build_absolute_uri(reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))

        token = paypal_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }

        data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(plan.id),
                    "amount": {
                        "currency_code": "USD",
                        "value": str(plan.price)
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "EXAMPLE INC",
                        "locale": "en-US",
                        "landing_page": "LOGIN",
                        # "shipping_preference": "New York, NY",
                        "user_action": "PAY_NOW",
                        "return_url": return_url,
                        "cancel_url": cancel_url
                    }
                }
            }
        }
        try:
            response = requests.post(
                'https://api-m.sandbox.paypal.com/v2/checkout/orders',
                headers=headers,
                data=json.dumps(data)
            )
            response_data = response.json()
            if response.status_code == 200:
                approval_url = next(link['href'] for link in response_data['links'] if link['rel'] == 'payer-action')
                return Response(
                    {'approval_url': approval_url}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': response_data}, status=response.status_code
                )
        except request.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
