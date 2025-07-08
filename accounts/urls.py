from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/me/', views.UserDetailView.as_view(), name='user-me'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # User approval (admin only)
    path('users/<int:pk>/approve/', views.UserApprovalView.as_view(), name='user-approve'),
    path('users/pending/', views.PendingUsersView.as_view(), name='pending-users'),
    
    # User profiles
    path('profiles/<int:pk>/', views.UserProfileView.as_view(), name='profile-detail'),
    path('profiles/me/', views.UserProfileView.as_view(), name='profile-me'),
]
