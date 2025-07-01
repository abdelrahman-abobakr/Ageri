from rest_framework import permissions
from .models import UserRole


class IsAdminUser(permissions.BasePermission):
    """
    Permission class for admin users only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == UserRole.ADMIN
        )


class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Permission class for moderators and admins
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.ADMIN, UserRole.MODERATOR]
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows owners to access their own data or admins to access any data
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Check if the object has a 'user' attribute (for profiles, etc.)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For User objects, check if it's the same user
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsApprovedUser(permissions.BasePermission):
    """
    Permission class that only allows approved users
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_approved
        )


class IsResearcherOrAbove(permissions.BasePermission):
    """
    Permission class for researchers, moderators, and admins
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.RESEARCHER, UserRole.MODERATOR, UserRole.ADMIN]
        )


class CanApproveUsers(permissions.BasePermission):
    """
    Permission class for users who can approve other users (admins only)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_approve_users()
        )


class CanCreateContent(permissions.BasePermission):
    """
    Permission class for users who can create content (moderators and admins)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_create_content()
        )
