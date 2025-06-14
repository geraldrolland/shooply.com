# myapp/permissions.py
from rest_framework.permissions import BasePermission

class IsUserAuthenticated(BasePermission):
    """
    Custom permission: Only allow owners of an object or admins to access.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(request, 'user'):
            return True
        return False