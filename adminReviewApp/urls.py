from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminReviewViewSet

app_name = 'admin_review'

router = DefaultRouter()
router.register(r'publications', AdminReviewViewSet, basename='admin-review')

urlpatterns = [
    path('', include(router.urls)),
]