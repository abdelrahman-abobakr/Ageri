from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from research.models import Publication
from .serializers import (
    PublicationReviewSerializer,
    PublicationListSerializer,
    PublicationApprovalSerializer,
    PublicationRejectionSerializer,
    PublicationPublishSerializer
)
from .permissions import IsAdminUser


class AdminReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for admin publication review functionality
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'abstract', 'research_area', 'keywords']
    filterset_fields = ['publication_type', 'research_area', 'is_featured']
    ordering_fields = ['submitted_at', 'title', 'priority']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        """Get queryset with optimized queries"""
        return Publication.objects.select_related(
            'submitted_by', 'reviewed_by', 'corresponding_author'
        ).prefetch_related(
            'author_assignments__author'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list' or self.action == 'pending':
            return PublicationListSerializer
        return PublicationReviewSerializer
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """List all publications with status = pending"""
        queryset = self.get_queryset().filter(status='pending')
        
        # Apply filters and search
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PublicationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PublicationListSerializer(queryset, many=True, context={'request': request})
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a publication"""
        publication = get_object_or_404(Publication, pk=pk)
        
        # Validate current status
        if publication.status != 'pending':
            return Response(
                {'error': f'Cannot approve publication with status "{publication.status}". Only pending publications can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PublicationApprovalSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Update publication
                publication.status = 'approved'
                publication.reviewed_by = request.user
                publication.reviewed_at = timezone.now()
                publication.review_notes = serializer.validated_data.get('review_notes', '')
                publication.save()
            
            # Return updated publication data
            response_serializer = PublicationReviewSerializer(
                publication, 
                context={'request': request}
            )
            return Response({
                'message': 'Publication approved successfully',
                'publication': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a publication"""
        publication = get_object_or_404(Publication, pk=pk)
        
        # Validate current status
        if publication.status != 'pending':
            return Response(
                {'error': f'Cannot reject publication with status "{publication.status}". Only pending publications can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PublicationRejectionSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Update publication
                publication.status = 'rejected'
                publication.reviewed_by = request.user
                publication.reviewed_at = timezone.now()
                publication.review_notes = serializer.validated_data['review_notes']
                publication.save()
            
            # Return updated publication data
            response_serializer = PublicationReviewSerializer(
                publication, 
                context={'request': request}
            )
            return Response({
                'message': 'Publication rejected successfully',
                'publication': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an approved publication"""
        publication = get_object_or_404(Publication, pk=pk)
        
        # Validate current status
        if publication.status != 'approved':
            return Response(
                {'error': f'Cannot publish publication with status "{publication.status}". Only approved publications can be published.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PublicationPublishSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Update publication
                publication.status = 'published'
                publication.is_public = True
                publication.is_featured = serializer.validated_data.get('is_featured', False)
                publication.priority = serializer.validated_data.get('priority', 0)
                publication.save()
            
            # Return updated publication data
            response_serializer = PublicationReviewSerializer(
                publication, 
                context={'request': request}
            )
            return Response({
                'message': 'Publication published successfully',
                'publication': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get review statistics"""
        from django.db.models import Count, Q
        
        stats = Publication.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            approved=Count('id', filter=Q(status='approved')),
            rejected=Count('id', filter=Q(status='rejected')),
            published=Count('id', filter=Q(status='published')),
            draft=Count('id', filter=Q(status='draft'))
        )
        
        # Recent activity (last 30 days)
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=30)
        recent_stats = Publication.objects.filter(
            submitted_at__gte=recent_date
        ).aggregate(
            recent_submissions=Count('id'),
            recent_approvals=Count('id', filter=Q(reviewed_at__gte=recent_date, status='approved')),
            recent_rejections=Count('id', filter=Q(reviewed_at__gte=recent_date, status='rejected'))
        )
        
        return Response({
            'overview': stats,
            'recent_activity': recent_stats,
            'pending_requiring_attention': stats['pending']
        })