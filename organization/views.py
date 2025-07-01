from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, F

from accounts.permissions import IsAdminUser, IsModeratorOrAdmin, IsApprovedUser
from .models import Department, Lab, ResearcherAssignment
from .serializers import (
    DepartmentSerializer, DepartmentListSerializer,
    LabSerializer, LabListSerializer,
    ResearcherAssignmentSerializer, ResearcherAssignmentListSerializer
)


class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    List all departments or create a new department
    """
    queryset = Department.objects.all().select_related('head')
    permission_classes = [IsApprovedUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description', 'head__email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DepartmentListSerializer
        return DepartmentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsApprovedUser()]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a department
    """
    queryset = Department.objects.all().select_related('head')
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsApprovedUser()]
        return [IsAdminUser()]


class LabListCreateView(generics.ListCreateAPIView):
    """
    List all labs or create a new lab
    """
    queryset = Lab.objects.all().select_related('department', 'head')
    permission_classes = [IsApprovedUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'status']
    search_fields = ['name', 'description', 'department__name', 'head__email']
    ordering_fields = ['name', 'created_at', 'capacity']
    ordering = ['department__name', 'name']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LabListSerializer
        return LabSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsModeratorOrAdmin()]
        return [IsApprovedUser()]


class LabDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a lab
    """
    queryset = Lab.objects.all().select_related('department', 'head')
    serializer_class = LabSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsApprovedUser()]
        return [IsModeratorOrAdmin()]


class LabsByDepartmentView(generics.ListAPIView):
    """
    List labs by department
    """
    serializer_class = LabListSerializer
    permission_classes = [IsApprovedUser]

    def get_queryset(self):
        department_id = self.kwargs['department_id']
        return Lab.objects.filter(department_id=department_id).select_related('department', 'head')


class ResearcherAssignmentListCreateView(generics.ListCreateAPIView):
    """
    List all researcher assignments or create a new assignment
    """
    queryset = ResearcherAssignment.objects.all().select_related(
        'researcher', 'lab', 'department', 'assigned_by'
    )
    permission_classes = [IsApprovedUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['lab', 'department', 'status', 'researcher']
    search_fields = [
        'researcher__email', 'researcher__first_name', 'researcher__last_name',
        'lab__name', 'department__name', 'position'
    ]
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ResearcherAssignmentListSerializer
        return ResearcherAssignmentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsModeratorOrAdmin()]
        return [IsApprovedUser()]


class ResearcherAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a researcher assignment
    """
    queryset = ResearcherAssignment.objects.all().select_related(
        'researcher', 'lab', 'department', 'assigned_by'
    )
    serializer_class = ResearcherAssignmentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsApprovedUser()]
        return [IsModeratorOrAdmin()]


class MyAssignmentsView(generics.ListAPIView):
    """
    List current user's lab assignments
    """
    serializer_class = ResearcherAssignmentListSerializer
    permission_classes = [IsApprovedUser]

    def get_queryset(self):
        return ResearcherAssignment.objects.filter(
            researcher=self.request.user
        ).select_related('lab', 'department', 'assigned_by')


class LabAvailabilityView(APIView):
    """
    Check lab availability and capacity
    """
    permission_classes = [IsApprovedUser]

    def get(self, request, lab_id):
        try:
            lab = Lab.objects.get(id=lab_id)
            return Response({
                'lab_id': lab.id,
                'lab_name': lab.name,
                'capacity': lab.capacity,
                'current_researchers': lab.current_researchers_count,
                'available_spots': lab.available_spots,
                'is_at_capacity': lab.is_at_capacity,
                'status': lab.status
            })
        except Lab.DoesNotExist:
            return Response(
                {'error': 'Lab not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsApprovedUser])
def organization_stats(request):
    """
    Get organization statistics
    """
    from accounts.models import User, UserRole

    stats = {
        'departments': {
            'total': Department.objects.count(),
            'active': Department.objects.filter(status='active').count(),
        },
        'labs': {
            'total': Lab.objects.count(),
            'active': Lab.objects.filter(status='active').count(),
            'at_capacity': Lab.objects.filter(
                researcher_assignments__status='active'
            ).annotate(
                current_count=Count('researcher_assignments')
            ).filter(current_count__gte=F('capacity')).count(),
        },
        'assignments': {
            'total': ResearcherAssignment.objects.count(),
            'active': ResearcherAssignment.objects.filter(status='active').count(),
        },
        'researchers': {
            'total': User.objects.filter(role=UserRole.RESEARCHER).count(),
            'approved': User.objects.filter(
                role=UserRole.RESEARCHER, is_approved=True
            ).count(),
            'assigned': ResearcherAssignment.objects.filter(
                status='active'
            ).values('researcher').distinct().count(),
        }
    }

    return Response(stats)
