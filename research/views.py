
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Prefetch, Avg, Max, F, Case, When, Sum
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import exception_handler
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()

# Import permissions - make sure these exist in your accounts app
try:
    from accounts.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
except ImportError:
    # Fallback permissions if accounts app doesn't exist
    from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
    
    class IsAdminOrReadOnly(IsAuthenticated):
        def has_permission(self, request, view):
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            return request.user and request.user.is_authenticated and getattr(request.user, 'is_admin', False)
    
    class IsOwnerOrReadOnly(IsAuthenticated):
        def has_object_permission(self, request, view, obj):
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            return obj.submitted_by == request.user or request.user in obj.authors.all()

from .models import Publication, PublicationAuthor, PublicationMetrics
from .serializers import (
    PublicationListSerializer,
    PublicationDetailSerializer,
    PublicationCreateUpdateSerializer,
    PublicationApprovalSerializer,
    PublicationAuthorSerializer,
    PublicationMetricsSerializer,
    PublicationStatsSerializer,
    BulkActionSerializer,
    PublicationSearchSerializer
)

class PublicationViewSet(viewsets.ModelViewSet):
    """
    Enhanced ViewSet for managing publications with role-based permissions
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'status', 'publication_type', 'is_public', 'research_area',
        'authors', 'corresponding_author', 'submitted_by', 'is_featured'
    ]
    search_fields = [
        'title', 'abstract', 'keywords', 'journal_name', 'conference_name',
        'authors__first_name', 'authors__last_name', 'doi', 'research_area'
    ]
    ordering_fields = [
        'title', 'publication_date', 'created_at', 'updated_at',
        'citation_count', 'status', 'priority'
    ]
    ordering = ['-priority', '-publication_date', '-created_at']

    def get_queryset(self):
        """Enhanced queryset with optimizations"""
        queryset = Publication.objects.select_related(
            'submitted_by',
            'reviewed_by',
            'corresponding_author'
        ).prefetch_related(
            'authors',
            'author_assignments__author'
        ).annotate(
            author_count=Count('authors', distinct=True)
        )
        
        # Apply filters based on user permissions
        user = self.request.user
        if not user.is_authenticated:
            queryset = queryset.filter(status='published', is_public=True)
        elif not (hasattr(user, 'is_admin') and user.is_admin):
            queryset = queryset.filter(
                Q(status='published', is_public=True) |
                Q(submitted_by=user) |
                Q(authors=user)
            ).distinct()
        
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        serializer_map = {
            'list': PublicationListSerializer,
            'create': PublicationCreateUpdateSerializer,
            'update': PublicationCreateUpdateSerializer,
            'partial_update': PublicationCreateUpdateSerializer,
            'approve': PublicationApprovalSerializer,
            'statistics': PublicationStatsSerializer,
            'bulk_approve': BulkActionSerializer,
            'advanced_search': PublicationSearchSerializer,
        }
        return serializer_map.get(self.action, PublicationDetailSerializer)

    def get_permissions(self):
        """Enhanced permissions based on action"""
        permission_map = {
            'create': [IsAuthenticated()],
            'update': [IsAuthenticated(), IsOwnerOrReadOnly()],
            'partial_update': [IsAuthenticated(), IsOwnerOrReadOnly()],
            'destroy': [IsAuthenticated(), IsOwnerOrReadOnly()],
            'approve': [IsAuthenticated(), IsAdminUser()],
            'feature': [IsAuthenticated(), IsAdminUser()],
            'bulk_approve': [IsAuthenticated(), IsAdminUser()],
            'my_publications': [IsAuthenticated()],
            'validate_publication_data': [IsAuthenticated()],
            'check_doi': [permissions.AllowAny()],
            'featured': [permissions.AllowAny()],
            'recent': [permissions.AllowAny()],
            'stats': [permissions.AllowAny()],
        }
        
        return permission_map.get(self.action, [permissions.AllowAny()])

    def perform_create(self, serializer):
        """Enhanced creation with additional processing"""
        publication = serializer.save(submitted_by=self.request.user)
        
        # Clear relevant caches
        self._clear_publication_caches()
        
        return publication

    def perform_update(self, serializer):
        """Enhanced update with cache clearing"""
        serializer.save()
        self._clear_publication_caches()

    def perform_destroy(self, instance):
        """Enhanced deletion with cache clearing"""
        super().perform_destroy(instance)
        self._clear_publication_caches()

    def _clear_publication_caches(self):
        """Clear publication-related caches"""
        cache_keys = [
            'publication_stats',
            f'user_publications_{self.request.user.id}',
            'featured_publications',
            'recent_publications'
        ]
        cache.delete_many(cache_keys)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve or reject a publication"""
        publication = self.get_object()
        serializer = self.get_serializer(publication, data=request.data, partial=True)
        
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
                
                # Clear caches
                self._clear_publication_caches()
                
            return Response({
                'message': f'Publication {serializer.validated_data["status"]}',
                'publication': PublicationDetailSerializer(
                    publication, context={'request': request}
                ).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_publications(self, request):
        """Enhanced user publications with proper authentication checks"""
        # Strict authentication check
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Additional safety check for user ID
        if not hasattr(request.user, 'id') or request.user.id is None:
            return Response(
                {'error': 'Invalid user session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cache_key = f'user_publications_{request.user.id}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Use safe queryset filtering
                queryset = self.get_queryset().filter(
                    Q(submitted_by=request.user) | Q(authors=request.user)
                ).distinct()
                
                # Add pagination support
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = PublicationListSerializer(
                        page, many=True, context={'request': request}
                    )
                    paginated_response = self.get_paginated_response(serializer.data)
                    cached_data = paginated_response.data
                else:
                    serializer = PublicationListSerializer(
                        queryset, many=True, context={'request': request}
                    )
                    cached_data = serializer.data
                
                # Cache for 5 minutes
                cache.set(cache_key, cached_data, timeout=300)
            
            return Response(cached_data)
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error in my_publications: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve publications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        """Feature/unfeature a publication"""
        if not request.user.is_authenticated or not (hasattr(request.user, 'is_admin') and request.user.is_admin):
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        publication = self.get_object()
        publication.is_featured = not publication.is_featured
        publication.save()
        
        self._clear_publication_caches()
        
        return Response({
            'message': f'Publication {"featured" if publication.is_featured else "unfeatured"}',
            'is_featured': publication.is_featured
        })

    @action(detail=False, methods=['get'])
    def check_doi(self, request):
        """Check if DOI already exists in database"""
        doi = request.query_params.get('doi', '').strip()
        
        if not doi:
            return Response({
                'exists': False,
                'message': 'No DOI provided'
            })
        
        # Format validation
        if not doi.startswith('10.'):
            return Response({
                'exists': False,
                'valid_format': False,
                'message': "DOI must start with '10.'"
            })
        
        # Check if exists
        try:
            existing_pub = Publication.objects.get(doi=doi)
            return Response({
                'exists': True,
                'valid_format': True,
                'existing_publication': {
                    'id': existing_pub.id,
                    'title': existing_pub.title,
                    'authors': [author.username for author in existing_pub.authors.all()[:3]],
                    'publication_date': existing_pub.publication_date,
                    'status': existing_pub.status,
                    'url': f'/publications/{existing_pub.id}/'
                },
                'message': f"DOI already exists for: {existing_pub.title[:50]}..."
            })
        except Publication.DoesNotExist:
            return Response({
                'exists': False,
                'valid_format': True,
                'message': 'DOI is available'
            })

    @action(detail=False, methods=['post'])
    def validate_publication_data(self, request):
        """Validate publication data without saving"""
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                'valid': True,
                'message': 'All data is valid',
                'validated_data': serializer.validated_data
            })
        except serializers.ValidationError as e:
            return Response({
                'valid': False,
                'errors': e.detail,
                'message': 'Validation failed'
            }, status=400)

    def create(self, request, *args, **kwargs):
        """Enhanced create with better error handling"""
        print(f"📤 Received create request data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        
        try:
            print("🔍 Validating serializer...")
            serializer.is_valid(raise_exception=True)
            print("✅ Serializer validation passed")
            
            print("💾 Creating publication...")
            publication = self.perform_create(serializer)
            
            print(f"✅ Publication created successfully: {publication.id}")
            
            return Response({
                'success': True,
                'message': 'Publication created successfully',
                'data': PublicationDetailSerializer(
                    publication, context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            print(f"❌ Validation error: {e.detail}")
            
            # Transform validation errors for better frontend handling
            formatted_errors = self._format_validation_errors(e.detail)
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': formatted_errors,
                'error_type': 'validation'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An unexpected error occurred',
                'error': str(e),
                'error_type': 'server_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _format_validation_errors(self, errors):
        """Format validation errors for frontend consumption"""
        formatted = {}
        
        for field, field_errors in errors.items():
            if field == 'doi' and isinstance(field_errors[0], dict):
                # Special handling for DOI errors
                formatted[field] = {
                    'type': 'duplicate_doi',
                    'message': field_errors[0]['message'],
                    'existing_publication': field_errors[0].get('existing_publication'),
                    'suggestion': field_errors[0].get('suggestion')
                }
            else:
                # Standard field errors
                formatted[field] = {
                    'type': 'validation_error',
                    'messages': field_errors if isinstance(field_errors, list) else [str(field_errors)]
                }
        
        return formatted

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured publications"""
        try:
            cache_key = 'featured_publications'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                queryset = self.get_queryset().filter(
                    is_featured=True,
                    status='published',
                    is_public=True
                ).order_by('-priority', '-publication_date')[:10]
                
                serializer = PublicationListSerializer(
                    queryset, many=True, context={'request': request}
                )
                cached_data = serializer.data
                cache.set(cache_key, cached_data, timeout=600)  # 10 minutes
            
            return Response(cached_data)
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve featured publications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent publications"""
        try:
            cache_key = 'recent_publications'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                queryset = self.get_queryset().filter(
                    status='published',
                    is_public=True
                ).order_by('-publication_date', '-created_at')[:20]
                
                serializer = PublicationListSerializer(
                    queryset, many=True, context={'request': request}
                )
                cached_data = serializer.data
                cache.set(cache_key, cached_data, timeout=300)  # 5 minutes
            
            return Response(cached_data)
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve recent publications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get publication statistics"""
        try:
            cache_key = 'publication_stats'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                from django.db.models import Count, Sum
                
                stats = {
                    'total_publications': Publication.objects.filter(
                        status='published', is_public=True
                    ).count(),
                    'total_authors': User.objects.filter(
                        publications__status='published',
                        publications__is_public=True
                    ).distinct().count(),
                    'by_type': Publication.objects.filter(
                        status='published', is_public=True
                    ).values('publication_type').annotate(
                        count=Count('id')
                    ),
                    'total_citations': Publication.objects.filter(
                        status='published', is_public=True
                    ).aggregate(
                        total=Sum('citation_count')
                    )['total'] or 0
                }
                
                cached_data = stats
                cache.set(cache_key, cached_data, timeout=1800)  # 30 minutes
            
            return Response(cached_data)
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        """Bulk approve publications (admin only)"""
        if not request.user.is_authenticated or not (hasattr(request.user, 'is_admin') and request.user.is_admin):
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        publication_ids = request.data.get('publication_ids', [])
        action = request.data.get('action', 'approve')  # approve, reject, feature
        
        if not publication_ids:
            return Response(
                {'error': 'No publication IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                publications = Publication.objects.filter(id__in=publication_ids)
                
                if action == 'approve':
                    publications.update(status='published', is_public=True)
                elif action == 'reject':
                    publications.update(status='rejected')
                elif action == 'feature':
                    publications.update(is_featured=True)
                elif action == 'unfeature':
                    publications.update(is_featured=False)
                
                self._clear_publication_caches()
                
                return Response({
                    'message': f'{publications.count()} publications {action}d successfully',
                    'count': publications.count()
                })
        except Exception as e:
            return Response(
                {'error': f'Bulk operation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicationAuthorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing publication authors"""
    serializer_class = PublicationAuthorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['publication', 'author', 'is_corresponding', 'order']
    search_fields = ['author__username', 'author__email', 'publication__title']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    def get_queryset(self):
        """Enhanced queryset with permissions"""
        user = self.request.user

        queryset = PublicationAuthor.objects.select_related(
            'publication', 'author'
        ).prefetch_related('author__profile')

        if not user.is_authenticated:
            # Anonymous users see only public published publications
            return queryset.filter(
                publication__is_public=True, 
                publication__status='published'
            )
        elif hasattr(user, 'is_admin') and user.is_admin:
            return queryset
        else:
            # Users can only see author assignments for publications they have access to
            return queryset.filter(
                Q(publication__is_public=True, publication__status='published') |
                Q(publication__submitted_by=user) |
                Q(publication__authors=user)
            ).distinct()

    def perform_create(self, serializer):
        """Enhanced creation with validation"""
        publication = serializer.validated_data['publication']
        
        # Check if user can edit this publication
        if not publication.can_be_edited_by(self.request.user):
            raise permissions.PermissionDenied("You cannot edit this publication")
        
        serializer.save()

    def perform_update(self, serializer):
        """Enhanced update with validation"""
        publication = serializer.instance.publication
        
        # Check if user can edit this publication
        if not publication.can_be_edited_by(self.request.user):
            raise permissions.PermissionDenied("You cannot edit this publication")
        
        serializer.save()


class PublicationMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for publication metrics"""
    serializer_class = PublicationMetricsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['publication']
    ordering_fields = ['citation_count', 'view_count', 'download_count', 'updated_at']
    ordering = ['-citation_count']

    def get_queryset(self):
        """Get metrics for accessible publications"""
        user = self.request.user
        
        queryset = PublicationMetrics.objects.select_related('publication')
        
        if not user.is_authenticated:
            return queryset.filter(
                publication__is_public=True,
                publication__status='published'
            )
        elif hasattr(user, 'is_admin') and user.is_admin:
            return queryset
        else:
            return queryset.filter(
                Q(publication__is_public=True, publication__status='published') |
                Q(publication__submitted_by=user) |
                Q(publication__authors=user)
            ).distinct()

    def handle_exception(self, exc):
        """Enhanced exception handling with clearer messages"""
        if isinstance(exc, NotAuthenticated):
            return Response({
                'error': 'Authentication required',
                'message': 'Please log in to access this resource',
                'redirect': '/login/',
                'error_code': 'AUTH_REQUIRED'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if isinstance(exc, PermissionDenied):
            return Response({
                'error': 'Permission denied',
                'message': 'You do not have permission to perform this action',
                'error_code': 'PERMISSION_DENIED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().handle_exception(exc)
