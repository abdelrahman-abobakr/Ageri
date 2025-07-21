"""
URL configuration for research_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Language switching
    path('i18n/', include('django.conf.urls.i18n')),

    # API endpoints (not translated)
    path('api/auth/', include('accounts.urls')),
    path('api/organization/', include('organization.urls')),
    path('api/research/', include('research.urls')),
    path('api/content/', include('content.urls')),
    path('api/training/', include('training.urls')),
    path('api/services/', include('services.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Translated URLs
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path('dashboard/', include('dashboard.urls')),  # Custom admin dashboard
    path('rosetta/', include('rosetta.urls')),  # Translation management
    prefix_default_language=False,
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
