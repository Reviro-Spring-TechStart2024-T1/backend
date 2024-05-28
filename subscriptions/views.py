from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SubscriptionPlan, UserSubscription
from .serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionCreateSerializer,
    UserSubscriptionSerializer,
)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API for viewing subscription plans.
    '''
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]


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
