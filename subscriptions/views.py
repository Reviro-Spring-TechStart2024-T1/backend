import json

import requests

# from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_datetime

# from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status  # viewsets

# from rest_framework.decorators import action
from rest_framework.permissions import (  # IsAuthenticated,; IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (  # SubscriptionPlan,; UserSubscription,
    BillingCycle,
    FixedPrice,
    Frequency,
    PaymentPreferences,
    PayPalProduct,
    PayPalSubscriptionPlan,
    PricingScheme,
    Taxes,
)
from .serializers import (  # SubscriptionPlanSerializer,; UserSubscriptionCreateSerializer,; UserSubscriptionSerializer,
    CreatePaymentSerializer,
    CreatePayPalProductSerializer,
    PayPalSubscriptionSerializer,
    ProductsSerializer,
)
from .utils import paypal_token  # create_payment,; execute_payment,

# from menu.permissions import IsAdminOrReadOnly


# class CreatePaymentView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = CreatePaymentSerializer

#     @extend_schema(
#         summary='Create PayPal Payment',
#         description=(
#             'This view handles creating a PayPal payment.\n\n'
#             'Flow:\n'
#             '1. The user selects a subscription plan.\n'
#             "2. A PayPal payment is created with the plan's price.\n"
#             '3. The user is redirected to PayPal to approve the payment.'
#         ),
#         request=CreatePaymentSerializer,
#     )
#     def post(self, request):
#         serializer = CreatePaymentSerializer(data=request.data)
#         if serializer.is_valid():
#             plan_id = serializer.validated_data['plan_id']
#             try:
#                 plan = SubscriptionPlan.objects.get(id=plan_id)
#             except SubscriptionPlan.DoesNotExist:
#                 return Response({'error': 'Invalid plan_id'}, status=status.HTTP_400_BAD_REQUEST)

#         amount = plan.price
#         return_url = request.build_absolute_uri(reverse('execute-payment'))
#         cancel_url = request.build_absolute_uri(reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))
#         print('execute:', reverse('execute-payment'))
#         print('cancel:', reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))
#         payment = create_payment(amount, return_url, cancel_url)
#         if payment:
#             for link in payment['links']:
#                 if link['rel'] == 'approval_url':
#                     approval_url = link['href']
#                     return Response({'approval_url': approval_url}, status=status.HTTP_201_CREATED)
#         return Response({'error': 'Payment creation failed'}, status=status.HTTP_400_BAD_REQUEST)


# class ExecutePaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         summary='Execute PayPal Payment',
#         description=(
#             'This view handles executing the PayPal payment.\n\n'
#             'Flow:\n'
#             '1. After the user approves the payment on PayPal, they are redirected back to this view.\n'
#             '2. The payment details are verified.\n'
#             '3. A new subscription is created and associated with the user.'
#         ),
#         parameters=[
#             OpenApiParameter(
#                 name='paymentId',
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description='ID of the PayPal payment.'
#             ),
#             OpenApiParameter(
#                 name='PayerID',
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description='ID of the PayPal payer.'
#             ),
#         ],
#         responses={
#             200: OpenApiResponse(
#                 response=UserSubscriptionSerializer,
#                 description='Payment executed successfully and subscription created.'
#             ),
#             400: OpenApiResponse(description='Payment execution failed'),
#             500: OpenApiResponse(description='Internal server error'),
#         },
#     )
#     def get(self, request):
#         payment_id = request.query_params.get('paymentId')
#         payer_id = request.query_params.get('PayerID')
#         payment = execute_payment(payment_id, payer_id)
#         if payment:
#             try:
#                 transaction = payment['transactions'][0]
#                 plan_id = transaction['item_list']['items'][0]['sku']
#                 plan = get_object_or_404(SubscriptionPlan, id=plan_id)

#                 subscription = UserSubscription.objects.create(
#                     user=request.user,
#                     plan=plan,
#                     is_trial=False,
#                 )
#                 subscription.save()
#                 return Response({'status': 'Payment executed successfully'}, status=status.HTTP_200_OK)
#             except (KeyError, IndexError, SubscriptionPlan.DoesNotExist) as e:
#                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({'error': 'Payment execution failed'}, status=status.HTTP_400_BAD_REQUEST)


# class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
#     '''
#     API for viewing subscription plans.
#     '''
#     queryset = SubscriptionPlan.objects.all()
#     serializer_class = SubscriptionPlanSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]


# class UserSubscriptionViewSet(viewsets.ModelViewSet):
#     """
#     CRUD operations of the user subscriptions.
#     """
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         # Customers can only view their active subscriptions
#         return UserSubscription.objects.filter(user=self.request.user, is_active=True)

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UserSubscriptionCreateSerializer
#         return UserSubscriptionSerializer

#     def perform_destroy(self, instance):
#         # Destroy method to deactivate instead of deleting
#         instance.is_active = False
#         instance.save()

#     @action(detail=True, methods=['post'])
#     def extend(self, request, pk=None):
#         subscription = self.get_object()
#         additional_days = request.data.get(
#             'additional_days', subscription.plan.duration.days)  # Allow variable extension
#         subscription.extend_subscription(additional_days)
#         resp_data = {'status': 'subscription extended', 'end_date': subscription.end_date}
#         return Response(resp_data, status=status.HTTP_200_OK)

#     @action(detail=True, methods=['post'])
#     def cancel(self, request, pk=None):
#         subscription = self.get_object()
#         subscription.cancel_subscription()
#         resp_data = {'status': 'subscription canceled'}
#         return Response(resp_data, status=status.HTTP_200_OK)


# class CreateOrderViewV2PayPalAPI(APIView):
#     serializer_class = CreatePaymentSerializer

#     def post(self, request):
#         serializer = CreatePaymentSerializer(data=request.data)
#         if serializer.is_valid():
#             plan_id = serializer.validated_data['plan_id']
#             try:
#                 plan = SubscriptionPlan.objects.get(id=plan_id)
#             except SubscriptionPlan.DoesNotExist:
#                 return Response({'error': 'Invalid plan_id'}, status=status.HTTP_400_BAD_REQUEST)

#         return_url = request.build_absolute_uri(reverse('capture-order'))
#         cancel_url = request.build_absolute_uri(reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))

#         token = paypal_token()
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': 'Bearer ' + token,
#         }

#         data = {
#             "intent": "CAPTURE",
#             "purchase_units": [
#                 {
#                     "reference_id": str(plan.id),
#                     "amount": {
#                         "currency_code": "USD",
#                         "value": str(plan.price)
#                     }
#                 }
#             ],
#             "payment_source": {
#                 "paypal": {
#                     "experience_context": {
#                         "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
#                         "brand_name": "EXAMPLE INC",
#                         "locale": "en-US",
#                         "landing_page": "LOGIN",
#                         "shipping_preference": "NO_SHIPPING",
#                         "user_action": "PAY_NOW",
#                         "return_url": return_url,
#                         "cancel_url": cancel_url
#                     }
#                 }
#             }
#         }
#         try:
#             response = requests.post(
#                 'https://api-m.sandbox.paypal.com/v2/checkout/orders',
#                 headers=headers,
#                 data=json.dumps(data)
#             )
#             response_data = response.json()
#             if response.status_code == 200:
#                 approval_url = next(link['href'] for link in response_data['links'] if link['rel'] == 'payer-action')
#                 return Response(
#                     {'approval_url': approval_url}, status=status.HTTP_201_CREATED
#                 )
#             else:
#                 return Response(
#                     {'error': response_data}, status=response.status_code
#                 )
#         except request.RequestException as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CaputeOrderViewV2PayPalAPI(APIView):
#     def get(self, request):
#         token = paypal_token()
#         order_id = request.query_params.get('token')
#         capture_url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture'
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': 'Bearer ' + token
#         }
#         response = requests.post(capture_url, headers=headers)
#         return Response(response.json())


class CreateProductView(APIView):
    serializer_class = CreatePayPalProductSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreatePayPalProductSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            name = validated_data['name']
            description = validated_data['description']
            type = validated_data.get('type', 'SERVICE')
            category = validated_data.get('category', 'SOFTWARE')
            image_url = validated_data.get(
                'image_url', 'https://res.cloudinary.com/dftbppd43/image/upload/v1/media/accounts/avatars/LOGO_DrinkJoy_lic32d')
            home_url = validated_data.get('home_url', 'https://kunasyl-backender.org.kg/')

            token = paypal_token()  # Assuming this function is defined to get the PayPal token
            url = "https://api-m.sandbox.paypal.com/v1/catalogs/products"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            data = {
                "name": name,
                "description": description,
                "type": type,
                "category": category,
                "image_url": image_url,
                "home_url": home_url
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 201 or response.status_code == 200:
                response_data = response.json()
                print(response_data)
                product_id = response_data.get("id")
                create_time = parse_datetime(response_data.get("create_time"))
                links = response_data.get("links")

                # Save to the database
                PayPalProduct.objects.create(
                    product_id=product_id,
                    name=name,
                    description=description,
                    create_time=create_time,
                    links=links
                )

                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(response.json(), status=response.status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductsListView(generics.ListAPIView):
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    queryset = PayPalProduct.objects.all()


class ProductView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    queryset = PayPalProduct.objects.all()


class PayPalCreatePlanView(generics.ListCreateAPIView):
    queryset = PayPalSubscriptionPlan.objects.all()
    serializer_class = PayPalSubscriptionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use validated data from the serializer
        validated_data = serializer.validated_data
        token = paypal_token()

        # Prepare headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
        }

        # Prepare data for the PayPal API request
        data = {
            "product_id": validated_data.get('product_id'),
            "name": validated_data.get('name'),
            "description": validated_data.get('description'),
            "status": validated_data.get('status'),
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": bc['frequency']['interval_unit'],
                        "interval_count": bc['frequency']['interval_count']
                    },
                    "tenure_type": bc['tenure_type'],
                    "sequence": bc['sequence'],
                    "total_cycles": bc['total_cycles'],
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": bc['pricing_scheme']['fixed_price']['value'],
                            "currency_code": bc['pricing_scheme']['fixed_price']['currency_code']
                        }
                    } if bc.get('pricing_scheme') else None
                } for bc in validated_data['billing_cycles']
            ],
            "payment_preferences": {
                "auto_bill_outstanding": validated_data['payment_preferences']['auto_bill_outstanding'],
                "setup_fee": {
                    "value": validated_data['payment_preferences']['setup_fee']['value'],
                    "currency_code": validated_data['payment_preferences']['setup_fee']['currency_code']
                },
                "setup_fee_failure_action": validated_data['payment_preferences']['setup_fee_failure_action'],
                "payment_failure_threshold": validated_data['payment_preferences']['payment_failure_threshold']
            },
            "taxes": {
                "percentage": validated_data['taxes']['percentage'],
                "inclusive": validated_data['taxes']['inclusive']
            }
        }

        response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/plans',
                                 headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            response_data = response.json()

            # Parse and save payment preferences
            payment_preferences_data = response_data['payment_preferences']
            setup_fee_data = payment_preferences_data['setup_fee']
            setup_fee = FixedPrice.objects.create(**setup_fee_data)
            payment_preferences = PaymentPreferences.objects.create(
                setup_fee=setup_fee,
                auto_bill_outstanding=payment_preferences_data['auto_bill_outstanding'],
                setup_fee_failure_action=payment_preferences_data['setup_fee_failure_action'],
                payment_failure_threshold=payment_preferences_data['payment_failure_threshold']
            )

            # Parse and save taxes
            taxes_data = response_data['taxes']
            taxes = Taxes.objects.create(
                percentage=taxes_data['percentage'],
                inclusive=taxes_data['inclusive']
            )

            # Parse PayPal response and create the subscription
            subscription = PayPalSubscriptionPlan.objects.create(
                plan_id=response_data['id'],
                product_id=response_data['product_id'],
                name=response_data['name'],
                description=response_data['description'],
                status=response_data['status'],
            )

            # Parse and save billing cycles
            for bc in response_data['billing_cycles']:
                frequency_data = bc['frequency']
                frequency = Frequency.objects.create(**frequency_data)

                pricing_scheme_data = bc.get('pricing_scheme')
                if pricing_scheme_data:
                    fixed_price_data = pricing_scheme_data['fixed_price']
                    fixed_price = FixedPrice.objects.create(**fixed_price_data)
                    subscription.price = fixed_price.value
                    pricing_scheme = PricingScheme.objects.create(fixed_price=fixed_price)
                else:
                    pricing_scheme = None

                billing_cycle = BillingCycle.objects.create(
                    # subscription=subscription,
                    frequency=frequency,
                    tenure_type=bc['tenure_type'],
                    sequence=bc['sequence'],
                    total_cycles=bc['total_cycles'],
                    pricing_scheme=pricing_scheme
                )
                subscription.billing_cycles.add(billing_cycle)

            subscription.payment_preferences = payment_preferences
            subscription.taxes = taxes
            subscription.links = response_data['links']

            subscription.save()
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)


class CreateOrderViewV2PayPalAPI(APIView):
    serializer_class = CreatePaymentSerializer

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            plan_id = serializer.validated_data['plan_id']
            try:
                plan = PayPalSubscriptionPlan.objects.get(plan_id=plan_id)
            except PayPalSubscriptionPlan.DoesNotExist:
                return Response({'error': 'Invalid plan_id'}, status=status.HTTP_400_BAD_REQUEST)

        return_url = request.build_absolute_uri(reverse('capture-order'))
        # cancel_url = request.build_absolute_uri(reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))

        token = paypal_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }

        data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": plan.plan_id,
                    "amount": {
                        "currency_code": "USD",
                        "value": plan.price
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "DrinkJoy",
                        "locale": "en-US",
                        "landing_page": "LOGIN",
                        "shipping_preference": "NO_SHIPPING",
                        "user_action": "PAY_NOW",
                        "return_url": return_url,
                        "cancel_url": 'cancel_url'  # need to change
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


class CaputeOrderViewV2PayPalAPI(APIView):
    def get(self, request):
        token = paypal_token()
        order_id = request.query_params.get('token')
        capture_url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        response = requests.post(capture_url, headers=headers)
        return Response(response.json())


class CreatePayPalSubscriptionAPI(APIView):
    serializer_class = CreatePaymentSerializer

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            plan_id = serializer.validated_data['plan_id']
            try:
                plan = PayPalSubscriptionPlan.objects.get(plan_id=plan_id)
            except PayPalSubscriptionPlan.DoesNotExist:
                return Response({'error': 'Invalid plan_id'}, status=status.HTTP_400_BAD_REQUEST)

        return_url = request.build_absolute_uri(reverse('capture-subscription'))
        # cancel_url = request.build_absolute_uri(reverse('user-subscription-cancel', kwargs={'pk': request.user.id}))

        token = paypal_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        data = {
            "plan_id": plan.plan_id,
            # "quantity": "20",
            # "shipping_amount": {
            #     "currency_code": "USD",
            #     "value": "10.00"
            # },
            # "subscriber": {
            #     "name": {
            #         "given_name": "John",
            #         "surname": "Doe"
            #     },
            #     "email_address": "customer@example.com",
            #     "shipping_address": {
            #         "name": {
            #             "full_name": "John Doe"
            #         },
            #         "address": {
            #             "address_line_1": "2211 N First Street",
            #             "address_line_2": "Building 17",
            #             "admin_area_2": "San Jose",
            #             "admin_area_1": "CA",
            #             "postal_code": "95131",
            #             "country_code": "US"
            #         }
            #     }
            # },
            "application_context": {
                "brand_name": "DrinkJoy",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                },
                "return_url": return_url,
                "cancel_url": "https://example.com/cancelUrl1"
            }
        }

        try:
            response = requests.post(
                'https://api-m.sandbox.paypal.com/v1/billing/subscriptions',
                headers=headers,
                data=json.dumps(data)
            )
            response_data = response.json()
            if response.status_code == 200 or response.status_code == 201:
                approval_url = next(link['href'] for link in response_data['links'] if link['rel'] == 'approve')
                self_url = next(link['href'] for link in response_data['links'] if link['rel'] == 'self')
                self_response = requests.get(self_url, headers=headers)
                return Response(
                    {'approval_url': approval_url, 'details': self_response.json()}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': response_data}, status=response.status_code
                )
        except request.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CaputePayPalSubscriptionAPI(APIView):
    def get(self, request):
        token = paypal_token()
        subscription_id = request.query_params.get('subscription_id')
        # ba_token = request.query_params.get('ba_token')
        # subs_token = request.query_params.get('token')
        get_url = f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{subscription_id}'
        # capture_url = f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{subscription_id}/capture'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        # data = {
        #     'note': 'Charging as the balance reached the limit',
        #     'capture_type': 'OUTSTANDING_BALANCE',
        #     'amount' : {
        #         'currency_code': 'USD',
        #         'value': '154.0'
        #     }
        # }
        response = requests.get(
            get_url,
            headers=headers,
            # data=json.dumps(data)
        )
        return Response(response.json())
