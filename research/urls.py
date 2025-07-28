
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'publications', views.PublicationViewSet, basename='publication')
router.register(r'publication-authors', views.PublicationAuthorViewSet, basename='publication-author')
router.register(r'publication-metrics', views.PublicationMetricsViewSet, basename='publication-metrics')

urlpatterns = [
    path('', include(router.urls)),
]
