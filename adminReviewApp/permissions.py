from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access admin review endpoints.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has admin role (assuming role field exists)
        if hasattr(request.user, 'role'):
            return request.user.role == 'admin'
        
        # Fallback to Django's is_staff or is_superuser
        return request.user.is_staff or request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)