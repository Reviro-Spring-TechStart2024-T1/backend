from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPartnerOrReadOnly(BasePermission):
    """
    Custom permission to allow only partners to create, update,
    partial update and delete objects but allow any user to view.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to partner users
        return request.user and request.user.role == 'partner'
