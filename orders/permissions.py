from rest_framework.permissions import BasePermission


class IsCustomerOnly(BasePermission):
    """
    Custom permission to allow only partners to create, update,
    partial update and delete objects but allow any user to view.
    """

    def has_permission(self, request, view):
        # Write permissions are only allowed to customer users
        return request.user and request.user.role == 'customer'
