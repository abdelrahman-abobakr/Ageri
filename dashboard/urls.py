from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_home, name='home'),
    
    # User management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:user_id>/reject/', views.reject_user, name='reject_user'),
    
    # Publication management
    path('publications/', views.publication_management, name='publication_management'),
    
    # Service requests
    path('service-requests/', views.service_requests, name='service_requests'),
    
    # System settings
    path('settings/', views.system_settings, name='system_settings'),
    path('organization-settings/', views.organization_settings, name='organization_settings'),

    # Enhanced admin management
    path('content/', views.content_management, name='content_management'),
    path('organization/', views.organization_management, name='organization_management'),
    path('training/', views.training_management, name='training_management'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('translations/', views.translation_management, name='translation_management'),

    # CRUD operations
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/<int:announcement_id>/edit/', views.edit_announcement, name='edit_announcement'),
    path('departments/create/', views.create_department, name='create_department'),
    path('labs/create/', views.create_lab, name='create_lab'),

    # API endpoints
    path('api/pending-counts/', views.api_pending_counts, name='api_pending_counts'),
]
