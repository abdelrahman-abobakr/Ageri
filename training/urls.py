from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, SummerTrainingViewSet, PublicServiceViewSet,
    CourseEnrollmentViewSet, SummerTrainingApplicationViewSet,
    PublicServiceRequestViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'summer-training', SummerTrainingViewSet)
router.register(r'public-services', PublicServiceViewSet)
router.register(r'enrollments', CourseEnrollmentViewSet)
router.register(r'applications', SummerTrainingApplicationViewSet)
router.register(r'service-requests', PublicServiceRequestViewSet)

app_name = 'training'

urlpatterns = [
    path('api/', include(router.urls)),
]
