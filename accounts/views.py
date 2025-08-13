from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import User, UserProfile, UserRole
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    UserApprovalSerializer, UserListSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, UserDetailSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin, IsApprovedUser


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint - creates new researcher accounts
    Enhanced like medical system
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': 'Registration successful. Please wait for admin approval.',
            'user': UserSerializer(user, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User login endpoint - returns JWT tokens
    Enhanced like medical system
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserDetailSerializer(user, context={'request': request}).data,
            'message': 'Login successful'
        })


class UserListView(generics.ListAPIView):
    """
    List all users - admin only
    Enhanced like medical system
    """
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserListSerializer
    # permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_approved', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'username', 'institution']
    ordering_fields = ['date_joined', 'email', 'last_name']
    ordering = ['-date_joined']


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):  # Changed from RetrieveUpdateAPIView
    """
    Retrieve, update, and delete user details
    Enhanced like medical system
    """
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserDetailSerializer
    # permission_classes = [IsOwnerOrAdmin]

    def get_object(self):
        # Check if this is the 'me' endpoint (no pk in kwargs)
        if 'pk' not in self.kwargs:
            return self.request.user
        return super().get_object()

    def retrieve(self, request, *args, **kwargs):
        """Enhanced retrieve with additional profile info"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Add extra context data
        data = serializer.data
        data['profile_completion'] = self._calculate_profile_completion(instance)
        data['last_login'] = instance.last_login
        
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        """Enhanced delete with additional checks and logging"""
        instance = self.get_object()
        
        # Prevent user from deleting themselves through the 'me' endpoint
        if 'pk' not in self.kwargs:  # This is the 'me' endpoint
            return Response({
                'error': 'You cannot delete your own account through this endpoint'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has admin permissions for deletion
        if not request.user.is_staff and not request.user.role == 'admin':
            return Response({
                'error': 'You do not have permission to delete users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Prevent admin from deleting themselves
        if instance == request.user:
            return Response({
                'error': 'You cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store user info for response
        user_email = instance.email
        user_name = instance.get_full_name() or instance.username
        
        # Perform the deletion
        self.perform_destroy(instance)
        
        return Response({
            'message': f'User "{user_name}" ({user_email}) has been successfully deleted',
            'deleted_user': {
                'id': kwargs.get('pk'),
                'email': user_email,
                'name': user_name
            }
        }, status=status.HTTP_200_OK)

    def _calculate_profile_completion(self, user):
        """Calculate profile completion percentage"""
        try:
            profile = user.profile
            total_fields = 8  # bio, research_interests, orcid, cv, website, linkedin, scholar, researchgate
            completed_fields = 0
            
            if profile.bio: completed_fields += 1
            if profile.research_interests: completed_fields += 1
            if profile.orcid_id: completed_fields += 1
            if profile.cv_file: completed_fields += 1
            if profile.website: completed_fields += 1
            if profile.linkedin: completed_fields += 1
            if profile.google_scholar: completed_fields += 1
            if profile.researchgate: completed_fields += 1
            
            return round((completed_fields / total_fields) * 100)
        except:
            return 0


class UserApprovalView(generics.UpdateAPIView):
    """
    Approve or reject user registration - admin only
    Enhanced like medical system
    """
    queryset = User.objects.all()
    serializer_class = UserApprovalSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['post', 'put', 'patch']

    def post(self, request, *args, **kwargs):
        """Handle POST requests by calling update"""
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, 
                                       context={'request': request})
        serializer.is_valid(raise_exception=True)

        # Handle both 'approved' and 'is_approved' field names
        approved = request.data.get('approved') or request.data.get('is_approved')
        if approved:
            instance.is_approved = True
            instance.approved_by = request.user
            instance.approval_date = timezone.now()
            message = f"User {instance.email} has been approved."
        else:
            instance.is_approved = False
            instance.approved_by = None
            instance.approval_date = None
            message = f"User {instance.email} approval has been revoked."

        instance.save()

        return Response({
            'message': message,
            'user': UserDetailSerializer(instance, context={'request': request}).data
        })


class PendingUsersView(generics.ListAPIView):
    """
    List users pending approval - admin only
    Enhanced like medical system
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name', 'username', 'institution']
    ordering = ['-date_joined']

    def get_queryset(self):
        return User.objects.filter(is_approved=False).select_related('profile')


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile
    Enhanced like medical system
    """
    queryset = UserProfile.objects.all()
    permission_classes = [IsOwnerOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_object(self):
        if self.kwargs.get('pk') == 'me' or 'pk' not in self.kwargs:
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            return profile
        return get_object_or_404(UserProfile, pk=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        """Enhanced update with proper multipart handling"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Convert multipart boolean strings to actual booleans
        data = request.data.copy()
        if 'is_public' in data:
            if isinstance(data['is_public'], str):
                data['is_public'] = data['is_public'].lower() in ['true', '1', 'yes']
        
        print(f"Original data: {request.data}")
        print(f"Processed data: {data}")
        print(f"Current is_public: {instance.is_public}")
        
        serializer = self.get_serializer(instance, data=data, 
                                       partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        print(f"Validated data: {serializer.validated_data}")
        
        # Perform the update
        self.perform_update(serializer)
        
        # Refresh from database
        instance.refresh_from_db()
        
        print(f"Final is_public: {instance.is_public}")
        
        # Return response with fresh data
        response_serializer = UserProfileSerializer(instance)
        return Response({
            'message': 'Profile updated successfully',
            'profile': response_serializer.data
        })


# Additional views for better user management
class UserProfilePublicView(generics.RetrieveAPIView):
    """
    Public view of user profiles (for researchers to view each other)
    """
    queryset = UserProfile.objects.filter(is_public=True)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only show public profiles or allow owners/admins to see private ones
        if not instance.is_public:
            if not (request.user == instance.user or request.user.is_admin):
                return Response(
                    {'error': 'This profile is private'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Add basic user info for public view
        data['user_info'] = {
            'full_name': instance.user.get_full_name(),
            'institution': instance.user.institution,
            'role': instance.user.role
        }
        
        return Response(data)


class ResearcherListView(generics.ListAPIView):
    """
    List all approved researchers (public directory)
    """
    serializer_class = UserListSerializer
    permission_classes = [IsApprovedUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'institution']
    search_fields = ['first_name', 'last_name', 'institution', 'profile__research_interests']
    ordering_fields = ['date_joined', 'last_name']
    ordering = ['last_name']

    def get_queryset(self):
        return User.objects.filter(
            is_approved=True, 
            is_active=True,
            profile__is_public=True
        ).select_related('profile')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout view that blacklists the refresh token
    Enhanced like medical system
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


# Profile statistics view (bonus feature)
class ProfileStatsView(APIView):
    """
    Get profile statistics for admins
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        stats = {
            'total_users': User.objects.count(),
            'approved_users': User.objects.filter(is_approved=True).count(),
            'pending_users': User.objects.filter(is_approved=False).count(),
            'users_by_role': {
                'admin': User.objects.filter(role=UserRole.ADMIN).count(),
                'moderator': User.objects.filter(role=UserRole.MODERATOR).count(),
                'researcher': User.objects.filter(role=UserRole.RESEARCHER).count(),
            },
            'profiles_complete': UserProfile.objects.exclude(
                bio='', research_interests=''
            ).count(),
            'public_profiles': UserProfile.objects.filter(is_public=True).count(),
        }
        
        return Response(stats)
