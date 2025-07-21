from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, F

from accounts.permissions import IsAdminUser, IsModeratorOrAdmin, IsApprovedUser
from .models import Department, Lab, ResearcherAssignment, OrganizationSettings
from .serializers import (
    DepartmentSerializer, DepartmentListSerializer, DepartmentInfoSerializer,
    LabSerializer, LabListSerializer, LabInfoSerializer,
    ResearcherAssignmentSerializer, ResearcherAssignmentListSerializer,
    OrganizationSettingsSerializer, OrganizationPublicSerializer
)


class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    List all departments or create a new department
    Public access for listing, admin required for creation
    """
    queryset = Department.objects.all().select_related('head')
    permission_classes = [permissions.AllowAny]
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
        """
        Allow public access for GET requests, require admin for POST
        """
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.AllowAny()]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a department
    Public access for viewing, admin required for modifications
    """
    queryset = Department.objects.all().select_related('head')
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminUser()]


class DepartmentInfoView(generics.RetrieveAPIView):
    """
    Get minimal department information with only labs and description
    Public access
    """
    queryset = Department.objects.all().prefetch_related(
        'labs__researcher_assignments__researcher',
        'labs__head'
    )
    serializer_class = DepartmentInfoSerializer
    permission_classes = [permissions.AllowAny]


class LabListCreateView(generics.ListCreateAPIView):
    """
    List all labs or create a new lab
    Public access for listing, admin required for creation
    """
    queryset = Lab.objects.all().select_related('department', 'head')
    permission_classes = [permissions.AllowAny]
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
        """
        Allow public access for GET requests, require admin for POST
        """
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.AllowAny()]


class LabDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a lab
    Public access for viewing, admin required for modifications
    """
    queryset = Lab.objects.all().select_related('department', 'head')
    serializer_class = LabSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminUser()]


class LabsByDepartmentView(generics.ListAPIView):
    """
    List labs by department (public access)
    """
    serializer_class = LabListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        department_id = self.kwargs['department_id']
        return Lab.objects.filter(department_id=department_id).select_related('department', 'head')


class LabResearchersView(generics.ListAPIView):
    """
    List researchers in a specific lab (public access)
    """
    serializer_class = ResearcherAssignmentListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        lab_id = self.kwargs['lab_id']
        return ResearcherAssignment.objects.filter(
            lab_id=lab_id,
            status='active'
        ).select_related('researcher', 'lab', 'department')


class LabHeadView(APIView):
    """
    Get the head researcher of a specific lab (public access)
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, lab_id):
        try:
            lab = Lab.objects.select_related('head').get(id=lab_id)
            if lab.head:
                from accounts.serializers import UserProfileSerializer
                serializer = UserProfileSerializer(lab.head, context={'request': request})
                return Response(serializer.data)
            else:
                return Response({'message': 'No head researcher assigned'}, status=status.HTTP_404_NOT_FOUND)
        except Lab.DoesNotExist:
            return Response({'error': 'Lab not found'}, status=status.HTTP_404_NOT_FOUND)


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


class LabResearcherManagementView(APIView):
    """
    Add or remove researchers from a lab
    """
    permission_classes = [IsModeratorOrAdmin]

    def post(self, request, lab_id):
        """Add a researcher to the lab"""
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            return Response(
                {'error': 'Lab not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        researcher_id = request.data.get('researcher_id')
        position = request.data.get('position', 'Researcher')
        start_date = request.data.get('start_date')
        notes = request.data.get('notes', '')

        if not researcher_id:
            return Response(
                {'error': 'researcher_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from accounts.models import User, UserRole
            researcher = User.objects.get(id=researcher_id, role=UserRole.RESEARCHER)

            if not researcher.is_approved:
                return Response(
                    {'error': 'Researcher must be approved'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if researcher is already assigned to this lab
            existing_assignment = ResearcherAssignment.objects.filter(
                researcher=researcher,
                lab=lab,
                status='active'
            ).first()

            if existing_assignment:
                return Response(
                    {'error': 'Researcher is already assigned to this lab'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check lab capacity
            if lab.is_at_capacity:
                return Response(
                    {'error': 'Lab is at full capacity'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create assignment
            assignment = ResearcherAssignment.objects.create(
                researcher=researcher,
                lab=lab,
                department=lab.department,
                start_date=start_date or timezone.now().date(),
                position=position,
                notes=notes,
                assigned_by=request.user,
                status='active'
            )

            # Return assignment details with researcher profile
            from .serializers import ResearcherAssignmentListSerializer
            serializer = ResearcherAssignmentListSerializer(assignment)

            return Response({
                'message': 'Researcher added successfully',
                'assignment': serializer.data
            }, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(
                {'error': 'Researcher not found or not authorized'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, lab_id):
        """Remove a researcher from the lab"""
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            return Response(
                {'error': 'Lab not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        researcher_id = request.data.get('researcher_id')
        if not researcher_id:
            return Response(
                {'error': 'researcher_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            assignment = ResearcherAssignment.objects.get(
                researcher_id=researcher_id,
                lab=lab,
                status='active'
            )

            # Set end date and deactivate
            assignment.end_date = timezone.now().date()
            assignment.status = 'inactive'
            assignment.save()

            return Response({
                'message': 'Researcher removed successfully',
                'assignment_id': assignment.id
            })

        except ResearcherAssignment.DoesNotExist:
            return Response(
                {'error': 'Assignment not found'},
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


class OrganizationSettingsView(APIView):
    """
    Get or update organization settings (singleton)
    Public access for GET, admin required for PUT/PATCH
    """

    def get_permissions(self):
        """
        Allow public access for GET requests, require admin for modifications
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    def get_object(self):
        """Get or create the singleton settings instance"""
        return OrganizationSettings.get_settings()

    def get(self, request):
        """Get organization settings"""
        settings = self.get_object()

        # Use public serializer for non-admin users
        if not request.user.is_authenticated or not request.user.is_staff:
            serializer = OrganizationPublicSerializer(settings)
        else:
            serializer = OrganizationSettingsSerializer(settings)

        return Response(serializer.data)

    def put(self, request):
        """Update organization settings"""
        settings = self.get_object()
        serializer = OrganizationSettingsSerializer(settings, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Partially update organization settings"""
        settings = self.get_object()
        serializer = OrganizationSettingsSerializer(
            settings, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
