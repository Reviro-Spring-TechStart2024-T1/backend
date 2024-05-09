from rest_framework.permissions import BasePermission


class IsCustomerOnly(BasePermission):
    """
    Custom permission to allow only authenticated customers to perform actions on endpoint.
    """

    def has_permission(self, request, view):
        # Write permissions are only allowed to customer users
        return request.user.is_authenticated and request.user.role == 'customer'


class IsPartnerOnly(BasePermission):
    """
    Custom permission to allow only authenticated partners to perform actions on endpoint.
    """

    def has_permission(self, request, view):
        # Write permissions are only allowed to customer users
        return request.user.is_authenticated and request.user.role == 'partner'
