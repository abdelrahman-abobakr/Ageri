from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, F

from accounts.permissions import IsModeratorOrAdmin, IsAdminOrReadOnly
from .models import TestService, Client, TechnicianAssignment, ServiceRequest
from .serializers import (
    TestServiceListSerializer, TestServiceDetailSerializer, TestServiceCreateUpdateSerializer,
    ClientListSerializer, ClientDetailSerializer, ClientCreateUpdateSerializer,
    TechnicianAssignmentSerializer, TechnicianAssignmentCreateUpdateSerializer,
    ServiceRequestListSerializer, ServiceRequestDetailSerializer, ServiceRequestCreateUpdateSerializer
)


class TestServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing test services
    """
    queryset = TestService.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'department', 'lab', 'status', 'is_featured', 'is_public']
    search_fields = ['name', 'description', 'service_code', 'tags']
    ordering_fields = ['name', 'created_at', 'base_price', 'max_concurrent_requests']
    ordering = ['-is_featured', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return TestServiceListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TestServiceCreateUpdateSerializer
        return TestServiceDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by availability - we'll filter this in Python since current_requests is a property
        if self.request.query_params.get('available_only') == 'true':
            queryset = queryset.filter(status='active')
            # Additional filtering will be done in the serializer or view

        # Filter by user role - check if user is authenticated first
        if self.request.user.is_authenticated and self.request.user.role == 'researcher':
            queryset = queryset.filter(is_public=True)

        return queryset.select_related('department', 'lab').prefetch_related('technician_assignments')

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def assign_technician(self, request, pk=None):
        """Assign a technician to a service"""
        service = self.get_object()
        technician_id = request.data.get('technician_id')
        role = request.data.get('role', 'primary')

        try:
            from accounts.models import User
            technician = User.objects.get(id=technician_id, role__in=['admin', 'moderator'])

            assignment, created = TechnicianAssignment.objects.get_or_create(
                service=service,
                technician=technician,
                defaults={'role': role}
            )

            if not created:
                assignment.role = role
                assignment.is_active = True
                assignment.save()

            serializer = TechnicianAssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(
                {'error': 'Technician not found or not authorized'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def remove_technician(self, request, pk=None):
        """Remove a technician from a service"""
        service = self.get_object()
        technician_id = request.data.get('technician_id')

        try:
            assignment = TechnicianAssignment.objects.get(
                service=service,
                technician_id=technician_id
            )
            assignment.is_active = False
            assignment.save()

            return Response({'message': 'Technician removed successfully'})

        except TechnicianAssignment.DoesNotExist:
            return Response(
                {'error': 'Assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get service statistics"""
        queryset = self.get_queryset()

        stats = {
            'total_services': queryset.count(),
            'active_services': queryset.filter(status='active').count(),
            'featured_services': queryset.filter(is_featured=True).count(),
            'services_by_category': dict(
                queryset.values('category').annotate(count=Count('id')).values_list('category', 'count')
            ),
            'average_price': queryset.filter(is_free=False).aggregate(
                avg_price=Avg('base_price')
            )['avg_price'] or 0,
            'total_requests': ServiceRequest.objects.filter(service__in=queryset).count(),
            'capacity_utilization': {
                'total_capacity': queryset.aggregate(total=Sum('max_concurrent_requests'))['total'] or 0,
                'current_usage': sum(service.current_requests for service in queryset),
            }
        }

        return Response(stats)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clients
    """
    queryset = Client.objects.all()
    permission_classes = [IsModeratorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['client_type', 'is_active', 'payment_terms']
    search_fields = ['name', 'organization', 'email', 'client_id']
    ordering_fields = ['name', 'registration_date', 'total_requests', 'total_spent']
    ordering = ['-registration_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ClientCreateUpdateSerializer
        return ClientDetailSerializer

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get client statistics"""
        queryset = self.get_queryset()

        stats = {
            'total_clients': queryset.count(),
            'active_clients': queryset.filter(is_active=True).count(),
            'clients_by_type': dict(
                queryset.values('client_type').annotate(count=Count('id')).values_list('client_type', 'count')
            ),
            'total_revenue': queryset.aggregate(total=Sum('total_spent'))['total'] or 0,
            'average_spending': queryset.aggregate(avg=Avg('total_spent'))['avg'] or 0,
            'top_clients': ClientListSerializer(
                queryset.order_by('-total_spent')[:5], many=True
            ).data
        }

        return Response(stats)


class ServiceRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service requests
    """
    queryset = ServiceRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'client', 'assigned_technician', 'status', 'priority', 'urgency', 'is_paid']
    search_fields = ['request_id', 'title', 'description']
    ordering_fields = ['requested_date', 'preferred_completion_date', 'priority', 'status']
    ordering = ['-requested_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceRequestListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ServiceRequestCreateUpdateSerializer
        return ServiceRequestDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by user role
        if self.request.user.role == 'researcher':
            # Researchers can only see requests they're assigned to
            queryset = queryset.filter(assigned_technician=self.request.user)

        return queryset.select_related('service', 'client', 'assigned_technician', 'reviewed_by')

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def assign_technician(self, request, pk=None):
        """Assign a technician to a request"""
        service_request = self.get_object()
        technician_id = request.data.get('technician_id')

        try:
            from accounts.models import User
            technician = User.objects.get(id=technician_id, role__in=['admin', 'moderator', 'researcher'])

            service_request.assigned_technician = technician
            if service_request.status == 'approved':
                service_request.status = 'in_progress'
                service_request.started_date = timezone.now()
            service_request.save()

            serializer = self.get_serializer(service_request)
            return Response(serializer.data)

        except User.DoesNotExist:
            return Response(
                {'error': 'Technician not found or not authorized'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def start_request(self, request, pk=None):
        """Start working on a request"""
        service_request = self.get_object()

        if not service_request.can_be_started():
            return Response(
                {'error': 'Request cannot be started'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service_request.status = 'in_progress'
        service_request.started_date = timezone.now()
        service_request.save()

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_request(self, request, pk=None):
        """Mark request as completed"""
        service_request = self.get_object()

        if not service_request.can_be_completed():
            return Response(
                {'error': 'Request cannot be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service_request.status = 'completed'
        service_request.completed_date = timezone.now()

        # Update final cost if provided
        final_cost = request.data.get('final_cost')
        if final_cost:
            service_request.final_cost = final_cost

        service_request.save()

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def approve_request(self, request, pk=None):
        """Approve a service request"""
        service_request = self.get_object()

        if service_request.status != 'under_review':
            return Response(
                {'error': 'Only requests under review can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service_request.status = 'approved'
        service_request.reviewed_by = request.user
        service_request.review_date = timezone.now()
        service_request.review_notes = request.data.get('review_notes', '')

        # Set estimated cost if provided
        estimated_cost = request.data.get('estimated_cost')
        if estimated_cost:
            service_request.estimated_cost = estimated_cost

        service_request.save()

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def reject_request(self, request, pk=None):
        """Reject a service request"""
        service_request = self.get_object()

        if service_request.status not in ['submitted', 'under_review']:
            return Response(
                {'error': 'Only submitted or under review requests can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service_request.status = 'cancelled'
        service_request.reviewed_by = request.user
        service_request.review_date = timezone.now()
        service_request.review_notes = request.data.get('review_notes', '')
        service_request.save()

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get request statistics"""
        queryset = self.get_queryset()

        stats = {
            'total_requests': queryset.count(),
            'requests_by_status': dict(
                queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'requests_by_priority': dict(
                queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count')
            ),
            'overdue_requests': queryset.filter(
                preferred_completion_date__lt=timezone.now().date(),
                status__in=['submitted', 'under_review', 'approved', 'in_progress']
            ).count(),
            'total_revenue': queryset.filter(is_paid=True).aggregate(
                total=Sum('final_cost')
            )['total'] or 0,
            'pending_revenue': queryset.filter(
                is_paid=False,
                status__in=['completed', 'delivered']
            ).aggregate(total=Sum('final_cost'))['total'] or 0,
            'average_completion_time': queryset.filter(
                completed_date__isnull=False
            ).aggregate(
                avg_time=Avg('completed_date') - Avg('requested_date')
            )
        }

        return Response(stats)


class TechnicianAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing technician assignments
    """
    queryset = TechnicianAssignment.objects.all()
    permission_classes = [IsModeratorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'technician', 'role', 'is_active']
    search_fields = ['service__name', 'technician__first_name', 'technician__last_name']
    ordering_fields = ['start_date', 'total_completed', 'workload_percentage']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TechnicianAssignmentCreateUpdateSerializer
        return TechnicianAssignmentSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('service', 'technician')

    @action(detail=False, methods=['get'])
    def workload_report(self, request):
        """Get technician workload report"""
        queryset = self.get_queryset().filter(is_active=True)

        report = []
        for assignment in queryset:
            report.append({
                'technician': assignment.technician.get_full_name(),
                'service': assignment.service.name,
                'role': assignment.role,
                'current_requests': assignment.current_requests,
                'max_requests': assignment.max_concurrent_requests,
                'workload_percentage': assignment.workload_percentage,
                'total_completed': assignment.total_completed,
                'is_available': assignment.is_available
            })

        return Response(report)
