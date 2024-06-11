from rest_framework import serializers

from subscriptions.choices import PayPalProductChoices

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

# class SubscriptionPlanSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SubscriptionPlan
#         fields = [
#             'id',
#             'name',
#             'description',
#             'duration',
#             'price',
#             'free_trial_days'
#         ]


# class UserSubscriptionSerializer(serializers.ModelSerializer):
#     plan = SubscriptionPlanSerializer(read_only=True)
#     remaining_days = serializers.SerializerMethodField()

#     class Meta:
#         model = UserSubscription
#         fields = [
#             'id',
#             'user',
#             'plan',
#             'start_date',
#             'end_date',
#             'is_active',
#             'is_trial',
#             'remaining_days',
#         ]

#     def get_remaining_days(self, obj):
#         return obj.remaining_days()


# class UserSubscriptionCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserSubscription
#         fields = ['plan', 'is_trial']

#     def validate(self, attrs):
#         user = self.context['request'].user
#         plan = attrs['plan']
#         is_trial = attrs.get('is_trial', False)

#         # Check if user has already used a free trial
#         if is_trial and plan.free_trial_days > 0:
#             has_had_free_trial = UserSubscription.objects.filter(
#                 user=user,
#                 plan__free_trial_days__gt=0,
#                 is_trial=True
#             ).exists()
#             if has_had_free_trial:
#                 raise serializers.ValidationError('User has already used a free trial.')

#         return attrs

#     def create(self, validated_data):
#         user = self.context['request'].user
#         plan = validated_data['plan']
#         is_trial = validated_data.get('is_trial', False)

#         subscription = UserSubscription(
#             user=user,
#             plan=plan,
#             is_trial=is_trial,
#         )
#         subscription.save()
#         return subscription


class CreatePaymentSerializer(serializers.Serializer):
    plan_id = serializers.CharField()

    def validate_plan_id(self, value):
        if not PayPalSubscriptionPlan.objects.filter(plan_id=value).exists():
            raise serializers.ValidationError("Invalid plan_id")
        return value


class CreatePayPalProductSerializer(serializers.Serializer, PayPalProductChoices):

    name = serializers.CharField(max_length=255, required=True, help_text="The name of the product.")
    description = serializers.CharField(required=True, help_text="The description of the product.")
    product_type = serializers.ChoiceField(
        choices=PayPalProductChoices.PRODUCT_TYPE_CHOICES, default=PayPalProductChoices.SERVICE, required=False,
        help_text="The type of the product. More info can be found here: https://developer.paypal.com/docs/api/catalog-products/v1/"
    )
    category = serializers.ChoiceField(
        choices=PayPalProductChoices.PRODUCT_CATEGORY_CHOICES, default=PayPalProductChoices.SOFTWARE, required=False,
        help_text="The category of the product. More info can be found here: https://developer.paypal.com/docs/api/catalog-products/v1/"
    )
    image_url = serializers.URLField(
        required=False, default="https://res.cloudinary.com/dftbppd43/image/upload/v1/media/accounts/avatars/LOGO_DrinkJoy_lic32d", help_text="The URL of the product image.")
    home_url = serializers.URLField(required=False, default="https://kunasyl-backender.org.kg/",
                                    help_text="The home URL of the product.")


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPalProduct
        fields = [
            'id',
            'product_id',
            'name',
            'description',
            'create_time',
            'links'
        ]
        read_only_fields = [
            'product_id',
            'create_time',
            'links'
        ]


class FrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Frequency
        fields = ['interval_unit', 'interval_count']


class FixedPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedPrice
        fields = ['value', 'currency_code']


class PricingSchemeSerializer(serializers.ModelSerializer):
    fixed_price = FixedPriceSerializer()

    class Meta:
        model = PricingScheme
        fields = ['fixed_price']


class BillingCycleSerializer(serializers.ModelSerializer):
    frequency = FrequencySerializer()
    pricing_scheme = PricingSchemeSerializer(required=False)

    class Meta:
        model = BillingCycle
        fields = ['frequency', 'tenure_type', 'sequence', 'total_cycles', 'pricing_scheme']

    def create(self, validated_data):
        frequency_data = validated_data.pop('frequency')
        frequency = Frequency.objects.create(**frequency_data)

        pricing_scheme_data = validated_data.pop('pricing_scheme', None)
        if pricing_scheme_data:
            fixed_price_data = pricing_scheme_data.pop('fixed_price')
            fixed_price = FixedPrice.objects.create(**fixed_price_data)
            pricing_scheme = PricingScheme.objects.create(fixed_price=fixed_price)
        else:
            pricing_scheme = None

        billing_cycle = BillingCycle.objects.create(
            frequency=frequency, pricing_scheme=pricing_scheme, **validated_data)
        return billing_cycle

    def update(self, instance, validated_data):
        frequency_data = validated_data.pop('frequency')
        Frequency.objects.filter(id=instance.frequency.id).update(**frequency_data)

        pricing_scheme_data = validated_data.pop('pricing_scheme', None)
        if pricing_scheme_data:
            fixed_price_data = pricing_scheme_data.pop('fixed_price')
            FixedPrice.objects.filter(id=instance.pricing_scheme.fixed_price.id).update(**fixed_price_data)
            PricingScheme.objects.filter(id=instance.pricing_scheme.id).update(
                fixed_price=instance.pricing_scheme.fixed_price)
        elif instance.pricing_scheme:
            instance.pricing_scheme.delete()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PaymentPreferencesSerializer(serializers.ModelSerializer):
    setup_fee = FixedPriceSerializer()

    class Meta:
        model = PaymentPreferences
        fields = ['auto_bill_outstanding', 'setup_fee', 'setup_fee_failure_action', 'payment_failure_threshold']

    def create(self, validated_data):
        setup_fee_data = validated_data.pop('setup_fee')
        setup_fee = FixedPrice.objects.create(**setup_fee_data)
        payment_preferences = PaymentPreferences.objects.create(setup_fee=setup_fee, **validated_data)
        return payment_preferences


class TaxesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxes
        fields = ['percentage', 'inclusive']


class PayPalSubscriptionSerializer(serializers.ModelSerializer):
    billing_cycles = BillingCycleSerializer(many=True)
    payment_preferences = PaymentPreferencesSerializer()
    taxes = TaxesSerializer()

    class Meta:
        model = PayPalSubscriptionPlan
        fields = [
            'id',
            'plan_id',
            'product_id',
            'name',
            'description',
            'status',
            'billing_cycles',
            'payment_preferences',
            'taxes'
        ]
        read_only_fields = [
            'id',
            'plan_id',
        ]

    def create(self, validated_data):
        billing_cycles_data = validated_data.pop('billing_cycles')
        payment_preferences_data = validated_data.pop('payment_preferences')
        taxes_data = validated_data.pop('taxes')

        subscription = PayPalSubscriptionPlan.objects.create(**validated_data)

        # Create and add billing cycles
        for billing_cycle_data in billing_cycles_data:
            frequency_data = billing_cycle_data.pop('frequency')
            frequency = Frequency.objects.create(**frequency_data)

            pricing_scheme_data = billing_cycle_data.pop('pricing_scheme', None)
            if pricing_scheme_data:
                fixed_price_data = pricing_scheme_data.pop('fixed_price')
                fixed_price = FixedPrice.objects.create(**fixed_price_data)
                pricing_scheme = PricingScheme.objects.create(fixed_price=fixed_price)
            else:
                pricing_scheme = None

            billing_cycle = BillingCycle.objects.create(
                frequency=frequency, pricing_scheme=pricing_scheme, **billing_cycle_data)
            subscription.billing_cycles.add(billing_cycle)

        # Create payment preferences
        setup_fee_data = payment_preferences_data.pop('setup_fee')
        setup_fee = FixedPrice.objects.create(**setup_fee_data)
        payment_preferences = PaymentPreferences.objects.create(setup_fee=setup_fee, **payment_preferences_data)
        subscription.payment_preferences = payment_preferences

        # Create taxes
        taxes = Taxes.objects.create(**taxes_data)
        subscription.taxes = taxes

        subscription.save()
        return subscription

    def update(self, instance, validated_data):
        billing_cycles_data = validated_data.pop('billing_cycles')
        payment_preferences_data = validated_data.pop('payment_preferences')
        taxes_data = validated_data.pop('taxes')

        instance.billing_cycles.clear()
        for billing_cycle_data in billing_cycles_data:
            frequency_data = billing_cycle_data.pop('frequency')
            frequency = Frequency.objects.create(**frequency_data)

            pricing_scheme_data = billing_cycle_data.pop('pricing_scheme', None)
            if pricing_scheme_data:
                fixed_price_data = pricing_scheme_data.pop('fixed_price')
                fixed_price = FixedPrice.objects.create(**fixed_price_data)
                pricing_scheme = PricingScheme.objects.create(fixed_price=fixed_price)
            else:
                pricing_scheme = None

            billing_cycle = BillingCycle.objects.create(
                frequency=frequency, pricing_scheme=pricing_scheme, **billing_cycle_data)
            instance.billing_cycles.add(billing_cycle)

        setup_fee_data = payment_preferences_data.pop('setup_fee')
        FixedPrice.objects.filter(id=instance.payment_preferences.setup_fee.id).update(**setup_fee_data)
        PaymentPreferences.objects.filter(id=instance.payment_preferences.id).update(**payment_preferences_data)

        Taxes.objects.filter(id=instance.taxes.id).update(**taxes_data)

        instance.save()
        return instance
