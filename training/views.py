from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg

from accounts.permissions import IsModeratorOrAdmin, IsResearcherOrAbove
from .models import (
    Course, SummerTraining, PublicService,
    CourseEnrollment, SummerTrainingApplication, PublicServiceRequest
)
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    SummerTrainingListSerializer, SummerTrainingDetailSerializer,
    PublicServiceListSerializer, PublicServiceDetailSerializer,
    CourseEnrollmentSerializer, SummerTrainingApplicationSerializer,
    PublicServiceRequestSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing courses"""
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'training_type', 'difficulty_level', 'status', 'is_featured',
        'is_public', 'is_free', 'instructor', 'department'
    ]
    search_fields = ['title', 'course_code', 'description', 'tags']
    ordering_fields = ['start_date', 'created_at', 'price', 'current_enrollment']
    ordering = ['-is_featured', '-start_date']

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsModeratorOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return CourseListSerializer
        return CourseDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset().select_related(
            'instructor', 'department'
        ).prefetch_related('enrollments')

        # Non-admin users can only see published courses
        if not self.request.user.role in ['admin', 'moderator']:
            queryset = queryset.filter(status='published', is_public=True)

        return queryset

    def perform_create(self, serializer):
        """Set default values when creating course"""
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """Enroll user in course"""
        course = self.get_object()

        # Check if user can register
        if not course.can_register():
            return Response(
                {'error': 'Registration is not open for this course'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already enrolled
        if CourseEnrollment.objects.filter(course=course, student=request.user).exists():
            return Response(
                {'error': 'You are already enrolled in this course'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create enrollment
        enrollment = CourseEnrollment.objects.create(
            course=course,
            student=request.user,
            payment_amount=course.price if not course.is_free else 0
        )

        # Update course enrollment count
        course.current_enrollment += 1
        course.save(update_fields=['current_enrollment'])

        serializer = CourseEnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """Get course enrollments (admin/moderator only)"""
        if not request.user.role in ['admin', 'moderator']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        course = self.get_object()
        enrollments = course.enrollments.all().select_related('student')
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured courses"""
        queryset = self.get_queryset().filter(is_featured=True, status='published')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming courses"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            start_date__gt=today,
            status='published'
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SummerTrainingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing summer training programs"""
    queryset = SummerTraining.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'difficulty_level', 'status', 'is_featured', 'is_public',
        'is_paid', 'provides_certificate', 'supervisor', 'department', 'lab'
    ]
    search_fields = ['title', 'program_code', 'description', 'tags']
    ordering_fields = ['start_date', 'created_at', 'duration_weeks', 'current_enrollment']
    ordering = ['-is_featured', '-start_date']

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsModeratorOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SummerTrainingListSerializer
        return SummerTrainingDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset().select_related(
            'supervisor', 'department', 'lab'
        ).prefetch_related('applications')

        # Non-admin users can only see published programs
        if not self.request.user.role in ['admin', 'moderator']:
            queryset = queryset.filter(status='published', is_public=True)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        """Apply to summer training program"""
        program = self.get_object()

        # Check if user can apply
        if not program.can_apply():
            return Response(
                {'error': 'Applications are not open for this program'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already applied
        if SummerTrainingApplication.objects.filter(program=program, applicant=request.user).exists():
            return Response(
                {'error': 'You have already applied to this program'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create application with data from request
        serializer = SummerTrainingApplicationSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(program=program, applicant=request.user)

            # Update program enrollment count
            program.current_enrollment += 1
            program.save(update_fields=['current_enrollment'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """Get program applications (admin/moderator only)"""
        if not request.user.role in ['admin', 'moderator']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        program = self.get_object()
        applications = program.applications.all().select_related('applicant', 'reviewed_by')
        serializer = SummerTrainingApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured summer training programs"""
        queryset = self.get_queryset().filter(is_featured=True, status='published')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming summer training programs"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            start_date__gt=today,
            status='published'
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PublicServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing public services"""
    queryset = PublicService.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'service_category', 'status', 'is_featured', 'is_public',
        'is_ongoing', 'is_free', 'coordinator', 'department'
    ]
    search_fields = ['title', 'service_code', 'description', 'tags']
    ordering_fields = ['created_at', 'title', 'current_requests']
    ordering = ['-is_featured', 'title']

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsModeratorOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PublicServiceListSerializer
        return PublicServiceDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset().select_related(
            'coordinator', 'department'
        ).prefetch_related('requests')

        # Non-admin users can only see published services
        if not self.request.user.role in ['admin', 'moderator']:
            queryset = queryset.filter(status='published', is_public=True)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def request_service(self, request, pk=None):
        """Request a public service"""
        service = self.get_object()

        # Check if service allows requests
        if not service.can_request():
            return Response(
                {'error': 'This service is not currently available for requests'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create service request with data from request
        serializer = PublicServiceRequestSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(service=service, requester=request.user)

            # Update service request count
            service.current_requests += 1
            service.save(update_fields=['current_requests'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def requests(self, request, pk=None):
        """Get service requests (admin/moderator only)"""
        if not request.user.role in ['admin', 'moderator']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        service = self.get_object()
        requests = service.requests.all().select_related('requester', 'assigned_to')
        serializer = PublicServiceRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured public services"""
        queryset = self.get_queryset().filter(is_featured=True, status='published')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get currently available services"""
        queryset = self.get_queryset().filter(status='published')
        available_services = [service for service in queryset if service.is_available]
        serializer = self.get_serializer(available_services, many=True)
        return Response(serializer.data)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing course enrollments"""
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'payment_status', 'certificate_issued',
        'course__training_type', 'course'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 'student__email',
        'course__title', 'course__course_code'
    ]
    ordering_fields = ['enrollment_date', 'completion_date']
    ordering = ['-enrollment_date']

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset().select_related(
            'student', 'course'
        )

        # Regular users can only see their own enrollments
        if self.request.user.role not in ['admin', 'moderator']:
            queryset = queryset.filter(student=self.request.user)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def mark_completed(self, request, pk=None):
        """Mark enrollment as completed"""
        enrollment = self.get_object()
        enrollment.mark_completed()
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def issue_certificate(self, request, pk=None):
        """Issue certificate for completed enrollment"""
        enrollment = self.get_object()

        if enrollment.status != 'completed':
            return Response(
                {'error': 'Enrollment must be completed to issue certificate'},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment.certificate_issued = True
        enrollment.certificate_number = f"CERT-{enrollment.course.course_code}-{enrollment.id}"
        enrollment.save(update_fields=['certificate_issued', 'certificate_number'])

        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)


class SummerTrainingApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing summer training applications"""
    queryset = SummerTrainingApplication.objects.all()
    serializer_class = SummerTrainingApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'year_of_study', 'program__difficulty_level',
        'certificate_issued', 'program'
    ]
    search_fields = [
        'applicant__first_name', 'applicant__last_name', 'applicant__email',
        'program__title', 'program__program_code', 'university', 'major'
    ]
    ordering_fields = ['application_date', 'review_date', 'gpa']
    ordering = ['-application_date']

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset().select_related(
            'applicant', 'program', 'reviewed_by'
        )

        # Regular users can only see their own applications
        if self.request.user.role not in ['admin', 'moderator']:
            queryset = queryset.filter(applicant=self.request.user)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def approve(self, request, pk=None):
        """Approve application"""
        application = self.get_object()
        application.status = 'approved'
        application.reviewed_by = request.user
        application.review_date = timezone.now()
        application.review_notes = request.data.get('review_notes', '')
        application.save(update_fields=[
            'status', 'reviewed_by', 'review_date', 'review_notes'
        ])

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def reject(self, request, pk=None):
        """Reject application"""
        application = self.get_object()
        application.status = 'rejected'
        application.reviewed_by = request.user
        application.review_date = timezone.now()
        application.review_notes = request.data.get('review_notes', '')
        application.save(update_fields=[
            'status', 'reviewed_by', 'review_date', 'review_notes'
        ])

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def mark_completed(self, request, pk=None):
        """Mark application as completed"""
        application = self.get_object()

        if application.status != 'approved':
            return Response(
                {'error': 'Application must be approved to mark as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = 'completed'
        application.completion_date = timezone.now().date()
        application.final_evaluation = request.data.get('final_evaluation', '')
        application.save(update_fields=[
            'status', 'completion_date', 'final_evaluation'
        ])

        serializer = self.get_serializer(application)
        return Response(serializer.data)


class PublicServiceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing public service requests"""
    queryset = PublicServiceRequest.objects.all()
    serializer_class = PublicServiceRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'urgency_level', 'payment_required', 'payment_status',
        'service__service_category', 'service'
    ]
    search_fields = [
        'requester__first_name', 'requester__last_name', 'requester__email',
        'service__title', 'service__service_code', 'contact_person',
        'organization'
    ]
    ordering_fields = ['request_date', 'estimated_completion', 'urgency_level']
    ordering = ['-request_date']

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset().select_related(
            'requester', 'service', 'assigned_to'
        )

        # Regular users can only see their own requests
        if self.request.user.role not in ['admin', 'moderator']:
            queryset = queryset.filter(requester=self.request.user)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def approve(self, request, pk=None):
        """Approve service request"""
        service_request = self.get_object()
        service_request.status = 'approved'
        service_request.assigned_to = request.data.get('assigned_to') or request.user
        service_request.estimated_completion = request.data.get('estimated_completion')
        service_request.save(update_fields=[
            'status', 'assigned_to', 'estimated_completion'
        ])

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def mark_in_progress(self, request, pk=None):
        """Mark service request as in progress"""
        service_request = self.get_object()
        service_request.status = 'in_progress'
        service_request.save(update_fields=['status'])

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def mark_completed(self, request, pk=None):
        """Mark service request as completed"""
        service_request = self.get_object()
        service_request.mark_completed()
        service_request.results_summary = request.data.get('results_summary', '')
        service_request.save(update_fields=['results_summary'])

        # Update service request count
        service_request.service.current_requests -= 1
        service_request.service.save(update_fields=['current_requests'])

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit_feedback(self, request, pk=None):
        """Submit client feedback for completed request"""
        service_request = self.get_object()

        # Only requester can submit feedback
        if service_request.requester != request.user:
            return Response(
                {'error': 'Only the requester can submit feedback'},
                status=status.HTTP_403_FORBIDDEN
            )

        if service_request.status != 'completed':
            return Response(
                {'error': 'Request must be completed to submit feedback'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service_request.client_feedback = request.data.get('client_feedback', '')
        service_request.satisfaction_rating = request.data.get('satisfaction_rating')
        service_request.save(update_fields=['client_feedback', 'satisfaction_rating'])

        serializer = self.get_serializer(service_request)
        return Response(serializer.data)
