from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestServiceViewSet, ServiceImageViewSet

router = DefaultRouter()
router.register(r'test-services', TestServiceViewSet, basename='testservice')
router.register(r'service-images', ServiceImageViewSet, basename='serviceimage')

urlpatterns = [
    path('', include(router.urls)),
]