from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicationViewSet, PublicationAuthorViewSet, PublicationMetricsViewSet

app_name = 'research'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'publications', PublicationViewSet, basename='publication')
router.register(r'authors', PublicationAuthorViewSet, basename='publication-author')
router.register(r'metrics', PublicationMetricsViewSet, basename='publication-metrics')

urlpatterns = [
    path('', include(router.urls)),
]
