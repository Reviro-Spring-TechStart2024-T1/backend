import json

import requests
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.permissions import IsAdminOrReadOnly

from .models import (
    BillingCycle,
    FixedPrice,
    Frequency,
    PaymentPreferences,
    PayPalProduct,
    PayPalSubscriptionPlan,
    PricingScheme,
    Taxes,
    UserSubscription,
)
from .serializers import (
    CreatePaymentSerializer,
    CreatePayPalProductSerializer,
    PayPalSubscriptionSerializer,
    PlanActivateDeactivateSerializer,
    ProductsSerializer,
    UserSubscriptionSerializer,
)
from .utils import paypal_token


class CreateProductView(APIView):
    serializer_class = CreatePayPalProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        summary='Create product',
        description=(
            'This endpoint allows admin to create a product that is offered by platform. '
            'Example for a product is the Happy Hours service that is provided by DrinkJoy.\n'
            '- Requires authentication.\n'
            '- Permissions: Admin only.\n\n'
            '**Required fields:** name and description. '
            '**Fields with default values:** product_type, category, image_url, home_url.\n'
            '- `product_type` and `category` fields on the PayPal server are enums. '
            'More info can be found here: https://developer.paypal.com/docs/api/catalog-products/v1/\n'
            '- `image_url` the url or the image after cloudinary cleanings will be gone. '
            'When the product stage will come need to update this part.\n'
            '- `home_url` for now the backend servers url'
        )
    )
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

    @extend_schema(
        summary='Get products',
        description=(
            'List of products created by admin on our end and PayPal server.\n'
            '- Permission: Allowed to anyone.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductsSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = PayPalProduct.objects.all()

    @extend_schema(
        summary='Get product',
        description=(
            'Get a product by its id on our end.\n'
            '- Requires authentication.\n'
            '- Permission: Allowed to anyone.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Update product',
        description=(
            'Update a product by its id on our end.\n'
            '- Requires authentication.\n'
            '- Permission: Admin only.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update product',
        description=(
            'Partially update a product by its id on our end.\n'
            '- Requires authentication.\n'
            '- Permission: Admin only.'
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary='Delete product',
        description=(
            'Delete a product by its id on our end.\n'
            '- Requires authentication.\n'
            '- Permission: Admin only.'
        )
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PayPalCreatePlanView(generics.ListCreateAPIView):
    queryset = PayPalSubscriptionPlan.objects.all()
    serializer_class = PayPalSubscriptionSerializer
    permission_classes = [IsAdminOrReadOnly]

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
    # only active plans are shown

    def get_queryset(self):
        queryset = PayPalSubscriptionPlan.objects.filter(status=PayPalSubscriptionPlan.ACTIVE)
        return queryset

    @extend_schema(
        summary='Create plan',
        description=(
            'This endpoint allows admin to create plans that are also registered in PayPal\'s server. '
            'To be able to correctly create plans admins have to understand the REST API of PayPal.\n\n'
            'All the available info is accessible here: https://developer.paypal.com/docs/api/subscriptions/v1/#plans_create\n'
            '- Requires authentication.\n'
            '- Permissions: Admin only.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @extend_schema(
        summary='Get plans',
        description=(
            'List of plans that are stored on our end, with all info.\n'
            '- Requires authentication.\n'
            '- Permission: Allowed to anyone.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CreateOrderViewV2PayPalAPI(APIView):
    serializer_class = CreatePaymentSerializer

    @extend_schema(
        summary='Create order',
        description=(
            'Endpoint that allows to transfer user to the PayPal payment page for a **single order**.\n'
            'Not applicable to the logic of Subscription.\n'
            '- Permission: Allowed to anyone.'
        )
    )
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


class CaputeOrderViewV2PayPalAPI(generics.GenericAPIView):
    @extend_schema(
        summary='Capture order',
        description=(
            'Endpoint that allows to capture the PayPal payment for a **single order** from a user.\n'
            'Not applicable to the logic of Subscription.\n'
            '- Permission: Allowed to anyone.'
        ),
        exclude=True
    )
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

    @extend_schema(
        summary='Create subscription',
        description=(
            'Endpoint that allows to transfer user to the PayPal payment page to pay for the subscription. '
            'In the field `plan_id` need to pass the plan_id that is given from PayPal. Available at `subscriptions/plans/` through `GET` method.\n'
            '- Permission: Allowed to anyone.'
        )
    )
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            plan_id = serializer.validated_data['plan_id']
            try:
                plan = PayPalSubscriptionPlan.objects.get(plan_id=plan_id)
            except PayPalSubscriptionPlan.DoesNotExist:
                return Response({'error': 'Invalid plan_id'}, status=status.HTTP_400_BAD_REQUEST)

        return_url = request.build_absolute_uri(reverse('capture-subscription'))
        cancel_url = request.build_absolute_uri(reverse('paypal-plans'))

        token = paypal_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        data = {
            "plan_id": plan.plan_id,
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
                "cancel_url": cancel_url
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


class CaputePayPalSubscriptionAPI(generics.GenericAPIView):
    @extend_schema(
        summary='Capture subscription',
        description=(
            'Endpoint that allows to get users approval of PayPal payment for the subscription.\n'
            'After the payment is made PayPal sends three params to the endpoint: `subscription_id`, `ba_token` and `token`.\n'
            'For this endpoint only subscription_id is currently used to access GET method on the PayPal part.\n'
            '- Permission: Allowed to anyone.'
        ),
        exclude=True
    )
    def get(self, request):
        token = paypal_token()
        subscription_id = request.query_params.get('subscription_id')
        # ba_token = request.query_params.get('ba_token') # TODO: research for what is ba_token used
        # subs_token = request.query_params.get('token') # TODO: research for what is token used
        get_url = f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{subscription_id}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        response = requests.get(
            get_url,
            headers=headers,
        )
        return Response(response.json())


class UserSubscriptionView(generics.ListCreateAPIView):
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(
        summary='Get subscribed users list',
        description=(
            'Allows users to see the subscriptions registered on the DrinkJoy\'s backend.\n'
            'Logically better suited for the admin page to be used.\n'
            '- Requires authentication.\n'
            '- Permissions: Allowed to anyone.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Register subscribed user',
        description=(
            'Allows to register data sent by `/subscriptions/capture-subscription/` '
            'endpoint to the DrinkJoy\'s database.\n\n'
            'Please make sure that the fields `billing_info` and `links` expect json, '
            'whereas all the other fields expect string.\n'
            'Do not forget to include JWT access token in the header of request.\n'
            '- Requires authentication.\n'
            '- Permissions: Allowed to anyone.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserSubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    queryset = UserSubscription.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_subscription = UserSubscription.objects.filter(user=self.request.user).first()
        if user_subscription:
            return user_subscription
        else:
            raise PermissionDenied('You do not have a subscription.')

    @extend_schema(
        summary='Get subscribed user',
        description=(
            'Allows user to see their subscription registered on the DrinkJoy\'s backend.\n'
            '- Requires authentication.\n'
            '- Permissions: Allowed to anyone.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PlanActivateDeactivateView(APIView):
    serializer_class = PlanActivateDeactivateSerializer
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        summary='Plans status updates',
        description=(
            'Allows to update status of plans on our server and PayPal server. '
            'Available choices are in action enum that has only two action options:\n'
            '- `activate` - changes status of plan to `ACTIVE`, if previously it was inactive.\n'
            '- `deactivate` - changes status of plan to `INACTIVE`, if previously it was active.\n'
            '- Requires authentication.\n'
            '- Permission: Admin only.'
        )
    )
    def post(self, request):
        serializer = PlanActivateDeactivateSerializer(data=request.data)
        if serializer.is_valid():

            token = paypal_token()
            plan_id = serializer.validated_data['plan_id']
            action = serializer.validated_data['action']
            headers = {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
            plan_activate_url = f'https://api-m.sandbox.paypal.com/v1/billing/plans/{plan_id}/{action}'
            response = requests.post(plan_activate_url, headers=headers)
            if response.status_code != 204:
                return Response(
                    {'error': response.json(), 'detail': 'Error from PayPal server.'}, status=status.HTTP_409_CONFLICT,
                )
            our_plan = PayPalSubscriptionPlan.objects.get(plan_id=plan_id)
            if action == 'activate':
                our_plan.status = 'ACTIVE'
                our_plan.save()
                return Response(
                    {'detail': 'Plan is activated on our server and PayPal server.'}, status=status.HTTP_200_OK
                )
            our_plan.status = 'INACTIVE'
            our_plan.save()
            return Response(
                {'detail': 'Plan is deactivated on our server and PayPal server.'}, status=status.HTTP_200_OK
            )
