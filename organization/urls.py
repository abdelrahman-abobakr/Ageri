from django.urls import path
from . import views

app_name = 'organization'

urlpatterns = [
    # Department endpoints
    path('departments/', views.DepartmentListCreateView.as_view(), name='department-list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    
    # Lab endpoints
    path('labs/', views.LabListCreateView.as_view(), name='lab-list'),
    path('labs/<int:pk>/', views.LabDetailView.as_view(), name='lab-detail'),
    path('departments/<int:department_id>/labs/', views.LabsByDepartmentView.as_view(), name='labs-by-department'),
    path('labs/<int:lab_id>/researchers/', views.LabResearchersView.as_view(), name='lab-researchers'),
    path('labs/<int:lab_id>/head/', views.LabHeadView.as_view(), name='lab-head'),
    path('labs/<int:lab_id>/availability/', views.LabAvailabilityView.as_view(), name='lab-availability'),
    
    # Researcher assignment endpoints
    path('assignments/', views.ResearcherAssignmentListCreateView.as_view(), name='assignment-list'),
    path('assignments/<int:pk>/', views.ResearcherAssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/my/', views.MyAssignmentsView.as_view(), name='my-assignments'),
    
    # Statistics
    path('stats/', views.organization_stats, name='organization-stats'),

    # Organization settings
    path('settings/', views.OrganizationSettingsView.as_view(), name='organization-settings'),
]
