from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, F
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.permissions import IsModeratorOrAdmin, IsAdminOrReadOnly
from .models import TestService, ServiceImage
from .serializers import (
    TestServiceListSerializer, TestServiceDetailSerializer, TestServiceCreateUpdateSerializer,
    ServiceImageSerializer, ServiceImageUploadSerializer, ServiceImageUpdateSerializer,
    TestServiceWithImagesSerializer
)


class TestServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing test services
    """
    queryset = TestService.objects.all()
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_featured', 'is_free']
    search_fields = ['name', 'description', 'service_code', 'tags']
    ordering_fields = ['name', 'created_at', 'base_price']
    ordering = ['-is_featured', 'name']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'images', 'primary_image']:
            # Allow guests to list and view services and their images
            permission_classes = [AllowAny]
        elif self.action == 'statistics':
            # Allow authenticated users to view statistics
            permission_classes = [IsAuthenticated]
        else:
            # Create, update, delete, and custom actions require moderator/admin permissions
            permission_classes = [IsAuthenticated, IsModeratorOrAdmin]
        
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return TestServiceListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TestServiceCreateUpdateSerializer
        elif self.action == 'with_images':
            return TestServiceWithImagesSerializer
        return TestServiceDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by availability
        if self.request.query_params.get('available_only') == 'true':
            queryset = queryset.filter(status='active')

        # For guests (unauthenticated users), show all active services
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='active')

        return queryset

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def statistics(self, request):
        """Get service statistics - requires authentication"""
        queryset = self.get_queryset()

        stats = {
            'total_services': queryset.count(),
            'active_services': queryset.filter(status='active').count(),
            'inactive_services': queryset.filter(status='inactive').count(),
            'featured_services': queryset.filter(is_featured=True).count(),
            'free_services': queryset.filter(is_free=True).count(),
            'paid_services': queryset.filter(is_free=False).count(),
            'services_by_category': dict(
                queryset.values('category').annotate(count=Count('id')).values_list('category', 'count')
            ),
            'average_price': queryset.filter(is_free=False).aggregate(
                avg_price=Avg('base_price')
            )['avg_price'] or 0,
            'services_with_images': queryset.filter(featured_image__isnull=False).count(),
        }

        return Response(stats)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def upload_image(self, request, pk=None):
        """Upload additional images for a service"""
        service = self.get_object()
        
        serializer = ServiceImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.save(service=service)
            return Response(
                ServiceImageSerializer(image, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """Get all additional images for a service"""
        service = self.get_object()
        images = service.images.all()
        serializer = ServiceImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], permission_classes=[IsModeratorOrAdmin])
    def delete_image(self, request, pk=None):
        """Delete an additional service image"""
        service = self.get_object()
        image_id = request.data.get('image_id')
        
        try:
            image = service.images.get(id=image_id)
            image.delete()
            return Response({'message': 'Image deleted successfully'})
        except ServiceImage.DoesNotExist:
            return Response(
                {'error': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def set_primary_image(self, request, pk=None):
        """Set an image as primary for a service"""
        service = self.get_object()
        image_id = request.data.get('image_id')
        
        try:
            # Reset all images to non-primary
            service.images.update(is_primary=False)
            
            # Set the specified image as primary
            image = service.images.get(id=image_id)
            image.is_primary = True
            image.save()
            
            return Response({'message': 'Primary image set successfully'})
        except ServiceImage.DoesNotExist:
            return Response(
                {'error': 'Image not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def primary_image(self, request, pk=None):
        """Get the primary additional image for a service"""
        service = self.get_object()
        primary_image = service.images.filter(is_primary=True).first()
        
        if primary_image:
            serializer = ServiceImageSerializer(primary_image, context={'request': request})
            return Response(serializer.data)
        return Response(
            {'message': 'No primary image found for this service'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['get'])
    def with_images(self, request, pk=None):
        """Get service details with all images"""
        service = self.get_object()
        serializer = TestServiceWithImagesSerializer(service, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured services"""
        featured_services = self.get_queryset().filter(is_featured=True, status='active')
        page = self.paginate_queryset(featured_services)
        if page is not None:
            serializer = TestServiceListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = TestServiceListSerializer(featured_services, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get services grouped by category"""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': 'Category parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        services = self.get_queryset().filter(category=category, status='active')
        page = self.paginate_queryset(services)
        if page is not None:
            serializer = TestServiceListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = TestServiceListSerializer(services, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status of a service"""
        service = self.get_object()
        service.is_featured = not service.is_featured
        service.save()
        
        serializer = self.get_serializer(service)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def toggle_status(self, request, pk=None):
        """Toggle active/inactive status of a service"""
        service = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in ['active', 'inactive', 'pending']:
            service.status = new_status
            service.save()
            
            serializer = self.get_serializer(service)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Invalid status. Must be active, inactive, or pending'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class ServiceImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service images
    """
    queryset = ServiceImage.objects.all()
    serializer_class = ServiceImageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'is_primary']
    ordering = ['-is_primary', '-created_at']

    def get_serializer_class(self):
        if self.action in ['create']:
            return ServiceImageUploadSerializer
        elif self.action in ['update', 'partial_update']:
            return ServiceImageUpdateSerializer
        return ServiceImageSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('service')