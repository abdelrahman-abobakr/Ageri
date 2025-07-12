from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.shortcuts import get_object_or_404

from accounts.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .models import Publication, PublicationAuthor, PublicationMetrics
from .serializers import (
    PublicationListSerializer,
    PublicationDetailSerializer,
    PublicationCreateUpdateSerializer,
    PublicationApprovalSerializer,
    PublicationAuthorSerializer,
    PublicationMetricsSerializer
)


class PublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing publications with role-based permissions
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'status', 'publication_type', 'is_public', 'research_area',
        'authors', 'corresponding_author', 'submitted_by'
    ]
    search_fields = [
        'title', 'abstract', 'keywords', 'journal_name', 'conference_name',
        'authors__first_name', 'authors__last_name', 'doi'
    ]
    ordering_fields = [
        'title', 'publication_date', 'created_at', 'updated_at',
        'citation_count', 'status'
    ]
    ordering = ['-publication_date', '-created_at']

    def get_queryset(self):
        """Get queryset based on user permissions"""
        user = self.request.user

        # Base queryset with optimizations
        queryset = Publication.objects.select_related(
            'corresponding_author', 'submitted_by', 'reviewed_by'
        ).prefetch_related(
            Prefetch(
                'author_assignments',
                queryset=PublicationAuthor.objects.select_related('author').order_by('order')
            ),
            'authors',
            'metrics'
        )

        # Filter based on user role and authentication
        if not user.is_authenticated:
            # Anonymous users see only published public publications
            return queryset.filter(status='published', is_public=True)

        elif user.is_admin:
            # Admins see all publications
            return queryset

        elif user.is_moderator:
            # Moderators see public publications and their own
            return queryset.filter(
                Q(is_public=True) |
                Q(submitted_by=user) |
                Q(authors=user)
            ).distinct()

        else:  # Regular researchers
            # Researchers see public publications and their own
            return queryset.filter(
                Q(status='published', is_public=True) |
                Q(submitted_by=user) |
                Q(authors=user)
            ).distinct()

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PublicationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PublicationCreateUpdateSerializer
        elif self.action == 'approve':
            return PublicationApprovalSerializer
        else:
            return PublicationDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action in ['approve', 'bulk_approve']:
            permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Set submitted_by to current user on creation"""
        serializer.save(submitted_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminOrReadOnly])
    def approve(self, request, pk=None):
        """Approve or reject a publication"""
        publication = self.get_object()
        serializer = PublicationApprovalSerializer(
            publication,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': f'Publication {serializer.validated_data["status"]}',
                'publication': PublicationDetailSerializer(
                    publication, context={'request': request}
                ).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_publications(self, request):
        """Get current user's publications"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = self.get_queryset().filter(
            Q(submitted_by=request.user) | Q(authors=request.user)
        ).distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PublicationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PublicationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """Get publications pending admin review"""
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset().filter(status='pending')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PublicationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PublicationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        """Bulk approve/reject publications"""
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        publication_ids = request.data.get('publication_ids', [])
        action_type = request.data.get('action', 'approve')  # 'approve' or 'reject'
        review_notes = request.data.get('review_notes', '')

        if not publication_ids:
            return Response(
                {'error': 'publication_ids required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action_type not in ['approve', 'reject']:
            return Response(
                {'error': 'action must be "approve" or "reject"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get publications to update
        publications = Publication.objects.filter(
            id__in=publication_ids,
            status='pending'
        )

        if not publications.exists():
            return Response(
                {'error': 'No pending publications found with provided IDs'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update publications
        new_status = 'approved' if action_type == 'approve' else 'rejected'
        updated_count = publications.update(
            status=new_status,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
            review_notes=review_notes
        )

        return Response({
            'message': f'{updated_count} publications {action_type}d',
            'updated_count': updated_count
        })

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """Increment view count for a publication"""
        publication = self.get_object()

        # Get or create metrics
        metrics, created = PublicationMetrics.objects.get_or_create(
            publication=publication,
            defaults={'view_count': 0}
        )

        # Increment view count
        metrics.view_count += 1
        metrics.save()

        return Response({
            'message': 'View count incremented',
            'view_count': metrics.view_count
        })

    @action(detail=True, methods=['post'])
    def increment_download(self, request, pk=None):
        """Increment download count for a publication"""
        publication = self.get_object()

        # Get or create metrics
        metrics, created = PublicationMetrics.objects.get_or_create(
            publication=publication,
            defaults={'download_count': 0}
        )

        # Increment download count
        metrics.download_count += 1
        metrics.save()

        return Response({
            'message': 'Download count incremented',
            'download_count': metrics.download_count
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get publication statistics"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Base queryset
        queryset = self.get_queryset()

        # Calculate statistics
        stats = {
            'total_publications': queryset.count(),
            'published_publications': queryset.filter(status='published').count(),
            'pending_publications': queryset.filter(status='pending').count(),
            'draft_publications': queryset.filter(status='draft').count(),
            'by_type': {},
            'by_status': {},
            'recent_publications': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
        }

        # Publications by type
        for pub_type in Publication.objects.values_list('publication_type', flat=True).distinct():
            stats['by_type'][pub_type] = queryset.filter(publication_type=pub_type).count()

        # Publications by status
        for status_choice in ['draft', 'pending', 'approved', 'rejected', 'published']:
            stats['by_status'][status_choice] = queryset.filter(status=status_choice).count()

        # User-specific stats if authenticated
        if request.user.is_authenticated:
            user_publications = queryset.filter(
                Q(submitted_by=request.user) | Q(authors=request.user)
            ).distinct()

            stats['user_stats'] = {
                'my_publications': user_publications.count(),
                'my_published': user_publications.filter(status='published').count(),
                'my_pending': user_publications.filter(status='pending').count(),
                'my_drafts': user_publications.filter(status='draft').count(),
            }

        return Response(stats)


class PublicationAuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing publication authors
    """
    serializer_class = PublicationAuthorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['publication', 'author', 'is_corresponding', 'is_first_author', 'is_last_author']
    search_fields = ['author__first_name', 'author__last_name', 'author__email', 'role']
    ordering_fields = ['order', 'created_at']
    ordering = ['publication', 'order']

    def get_queryset(self):
        """Get queryset based on user permissions"""
        user = self.request.user

        queryset = PublicationAuthor.objects.select_related(
            'publication', 'author'
        )

        if not user.is_authenticated:
            # Anonymous users see only public published publications
            return queryset.filter(publication__is_public=True, publication__status='published')
        elif user.is_admin:
            return queryset
        else:
            # Users can only see author assignments for publications they have access to
            return queryset.filter(
                Q(publication__is_public=True, publication__status='published') |
                Q(publication__submitted_by=user) |
                Q(publication__authors=user)
            ).distinct()


class PublicationMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for publication metrics
    """
    serializer_class = PublicationMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['publication']
    ordering_fields = ['view_count', 'download_count', 'citation_count', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Get queryset based on user permissions"""
        user = self.request.user

        queryset = PublicationMetrics.objects.select_related('publication')

        if not user.is_authenticated:
            # Anonymous users see only public published publications
            return queryset.filter(publication__is_public=True, publication__status='published')
        elif user.is_admin:
            return queryset
        else:
            # Users can only see metrics for publications they have access to
            return queryset.filter(
                Q(publication__is_public=True, publication__status='published') |
                Q(publication__submitted_by=user) |
                Q(publication__authors=user)
            ).distinct()
