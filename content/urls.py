from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet, PostViewSet, CommentViewSet

app_name = 'content'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
