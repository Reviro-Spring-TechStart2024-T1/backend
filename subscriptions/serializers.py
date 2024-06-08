from rest_framework import serializers

from subscriptions.choices import PayPalProductChoices

from .models import PayPalProduct, SubscriptionPlan, UserSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'description',
            'duration',
            'price',
            'free_trial_days'
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'user',
            'plan',
            'start_date',
            'end_date',
            'is_active',
            'is_trial',
            'remaining_days',
        ]

    def get_remaining_days(self, obj):
        return obj.remaining_days()


class UserSubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['plan', 'is_trial']

    def validate(self, attrs):
        user = self.context['request'].user
        plan = attrs['plan']
        is_trial = attrs.get('is_trial', False)

        # Check if user has already used a free trial
        if is_trial and plan.free_trial_days > 0:
            has_had_free_trial = UserSubscription.objects.filter(
                user=user,
                plan__free_trial_days__gt=0,
                is_trial=True
            ).exists()
            if has_had_free_trial:
                raise serializers.ValidationError('User has already used a free trial.')

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        plan = validated_data['plan']
        is_trial = validated_data.get('is_trial', False)

        subscription = UserSubscription(
            user=user,
            plan=plan,
            is_trial=is_trial,
        )
        subscription.save()
        return subscription


class CreatePaymentSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        if not SubscriptionPlan.objects.filter(id=value).exists():
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
