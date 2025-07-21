from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestServiceViewSet, ClientViewSet, ServiceRequestViewSet, TechnicianAssignmentViewSet

router = DefaultRouter()
router.register(r'test-services', TestServiceViewSet, basename='testservice')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'requests', ServiceRequestViewSet, basename='servicerequest')
router.register(r'technician-assignments', TechnicianAssignmentViewSet, basename='technicianassignment')

urlpatterns = [
    path('', include(router.urls)),
]
