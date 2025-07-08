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
            request.user.role == UserRole.ADMIN and
            request.user.is_approved
        )


class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Permission class for moderators and admins
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.ADMIN, UserRole.MODERATOR] and
            request.user.is_approved
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows owners to access their own data or admins to access any data
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_approved
        )
    
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
            request.user.role in [UserRole.RESEARCHER, UserRole.MODERATOR, UserRole.ADMIN] and
            request.user.is_approved
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


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read access to all users but write access only to admins
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and approved
        if not (request.user and request.user.is_authenticated and request.user.is_approved):
            return False

        # Read permissions for approved users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for admin users
        return request.user.role == UserRole.ADMIN


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read access to all users but write access only to owners
    """
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin can access any object
        if request.user.role == UserRole.ADMIN:
            return True

        # Check if the object has a 'submitted_by' attribute (for publications, etc.)
        if hasattr(obj, 'submitted_by'):
            return obj.submitted_by == request.user

        # Check if the object has a 'user' attribute (for profiles, etc.)
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Check if the user is an author of the publication
        if hasattr(obj, 'authors'):
            return request.user in obj.authors.all()

        # For User objects, check if it's the same user
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id

        return False
