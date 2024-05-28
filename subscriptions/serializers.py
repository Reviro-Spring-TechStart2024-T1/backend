from rest_framework import serializers

from .models import SubscriptionPlan, UserSubscription


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
