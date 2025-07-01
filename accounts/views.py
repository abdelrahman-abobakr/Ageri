from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User, UserProfile, UserRole
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    UserApprovalSerializer, UserListSerializer, UserProfileSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint - creates new researcher accounts
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
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User login endpoint - returns JWT tokens
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
            'user': UserSerializer(user).data
        })


class UserListView(generics.ListAPIView):
    """
    List all users - admin only
    """
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_approved', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['date_joined', 'email', 'last_name']
    ordering = ['-date_joined']


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user details
    """
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()


class UserApprovalView(generics.UpdateAPIView):
    """
    Approve or reject user registration - admin only
    """
    queryset = User.objects.all()
    serializer_class = UserApprovalSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if request.data.get('is_approved'):
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
            'user': UserSerializer(instance).data
        })


class PendingUsersView(generics.ListAPIView):
    """
    List users pending approval - admin only
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(is_approved=False).select_related('profile')


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            return profile
        return super().get_object()
