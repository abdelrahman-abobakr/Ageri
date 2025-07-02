from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course, SummerTraining, PublicService,
    CourseEnrollment, SummerTrainingApplication, PublicServiceRequest
)

User = get_user_model()


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list view"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    enrollment_percentage = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    can_register = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'short_description', 'course_code', 'credits',
            'duration_hours', 'training_type', 'difficulty_level',
            'instructor_name', 'department_name', 'start_date', 'end_date',
            'registration_deadline', 'max_participants', 'current_enrollment',
            'enrollment_percentage', 'price', 'is_free', 'status',
            'is_featured', 'featured_image', 'is_registration_open',
            'is_full', 'can_register', 'created_at'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail view"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    enrollment_percentage = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    can_register = serializers.ReadOnlyField()
    enrollments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'short_description', 'course_code',
            'credits', 'duration_hours', 'training_type', 'difficulty_level',
            'instructor', 'instructor_name', 'department', 'department_name',
            'start_date', 'end_date', 'registration_deadline',
            'max_participants', 'min_participants', 'current_enrollment',
            'enrollment_percentage', 'enrollments_count', 'price', 'is_free',
            'status', 'is_featured', 'is_public', 'prerequisites',
            'materials_provided', 'featured_image', 'syllabus', 'tags',
            'is_registration_open', 'is_full', 'can_register',
            'created_at', 'updated_at'
        ]
    
    def get_enrollments_count(self, obj):
        """Get count of active enrollments"""
        return obj.enrollments.filter(status__in=['approved', 'completed']).count()


class SummerTrainingListSerializer(serializers.ModelSerializer):
    """Serializer for summer training list view"""
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    total_hours = serializers.ReadOnlyField()
    is_application_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    can_apply = serializers.ReadOnlyField()
    
    class Meta:
        model = SummerTraining
        fields = [
            'id', 'title', 'short_description', 'program_code',
            'duration_weeks', 'hours_per_week', 'total_hours',
            'difficulty_level', 'supervisor_name', 'department_name',
            'lab_name', 'start_date', 'end_date', 'application_deadline',
            'max_trainees', 'current_enrollment', 'is_paid',
            'stipend_amount', 'provides_certificate', 'status',
            'is_featured', 'featured_image', 'is_application_open',
            'is_full', 'can_apply', 'created_at'
        ]


class SummerTrainingDetailSerializer(serializers.ModelSerializer):
    """Serializer for summer training detail view"""
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    total_hours = serializers.ReadOnlyField()
    is_application_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    can_apply = serializers.ReadOnlyField()
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SummerTraining
        fields = [
            'id', 'title', 'description', 'short_description', 'program_code',
            'duration_weeks', 'hours_per_week', 'total_hours', 'difficulty_level',
            'supervisor', 'supervisor_name', 'department', 'department_name',
            'lab', 'lab_name', 'start_date', 'end_date', 'application_deadline',
            'max_trainees', 'min_trainees', 'current_enrollment',
            'applications_count', 'academic_requirements', 'skills_requirements',
            'learning_objectives', 'project_description', 'is_paid',
            'stipend_amount', 'provides_certificate', 'provides_recommendation',
            'status', 'is_featured', 'is_public', 'featured_image',
            'program_brochure', 'tags', 'is_application_open', 'is_full',
            'can_apply', 'created_at', 'updated_at'
        ]
    
    def get_applications_count(self, obj):
        """Get count of active applications"""
        return obj.applications.filter(status__in=['approved', 'completed']).count()


class PublicServiceListSerializer(serializers.ModelSerializer):
    """Serializer for public service list view"""
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    is_available = serializers.ReadOnlyField()
    is_at_capacity = serializers.ReadOnlyField()
    can_request = serializers.ReadOnlyField()
    
    class Meta:
        model = PublicService
        fields = [
            'id', 'title', 'short_description', 'service_code',
            'service_category', 'coordinator_name', 'department_name',
            'is_ongoing', 'start_date', 'end_date', 'max_concurrent_requests',
            'current_requests', 'is_free', 'base_price', 'estimated_turnaround',
            'status', 'is_featured', 'featured_image', 'contact_email',
            'contact_phone', 'location', 'is_available', 'is_at_capacity',
            'can_request', 'created_at'
        ]


class PublicServiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for public service detail view"""
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    is_available = serializers.ReadOnlyField()
    is_at_capacity = serializers.ReadOnlyField()
    can_request = serializers.ReadOnlyField()
    requests_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PublicService
        fields = [
            'id', 'title', 'description', 'short_description', 'service_code',
            'service_category', 'coordinator', 'coordinator_name',
            'department', 'department_name', 'is_ongoing', 'start_date',
            'end_date', 'max_concurrent_requests', 'current_requests',
            'requests_count', 'is_free', 'base_price', 'pricing_details',
            'eligibility_criteria', 'required_documents', 'process_description',
            'estimated_turnaround', 'status', 'is_featured', 'is_public',
            'contact_email', 'contact_phone', 'location', 'featured_image',
            'service_brochure', 'tags', 'is_available', 'is_at_capacity',
            'can_request', 'created_at', 'updated_at'
        ]
    
    def get_requests_count(self, obj):
        """Get count of active requests"""
        return obj.requests.filter(status__in=['approved', 'in_progress']).count()


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for course enrollments"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'course', 'course_title', 'course_code', 'student',
            'student_name', 'enrollment_date', 'status', 'payment_status',
            'payment_amount', 'payment_date', 'payment_reference',
            'grade', 'attendance_percentage', 'completion_date',
            'certificate_issued', 'certificate_number', 'notes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['enrollment_date', 'payment_date', 'completion_date']
    
    def validate(self, data):
        """Validate enrollment data"""
        course = data.get('course')
        student = data.get('student', self.context['request'].user)
        
        # Check if course allows registration
        if course and not course.can_register():
            raise serializers.ValidationError("Registration is not open for this course")
        
        # Check for duplicate enrollment
        if CourseEnrollment.objects.filter(course=course, student=student).exists():
            raise serializers.ValidationError("You are already enrolled in this course")
        
        return data


class SummerTrainingApplicationSerializer(serializers.ModelSerializer):
    """Serializer for summer training applications"""
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    program_title = serializers.CharField(source='program.title', read_only=True)
    program_code = serializers.CharField(source='program.program_code', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = SummerTrainingApplication
        fields = [
            'id', 'program', 'program_title', 'program_code', 'applicant',
            'applicant_name', 'application_date', 'status', 'university',
            'major', 'year_of_study', 'gpa', 'motivation_letter',
            'relevant_experience', 'skills_and_interests', 'cv_file',
            'transcript', 'recommendation_letter', 'reviewed_by',
            'reviewed_by_name', 'review_date', 'review_notes',
            'start_date', 'completion_date', 'final_evaluation',
            'certificate_issued', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'program', 'applicant', 'application_date', 'reviewed_by', 'review_date',
            'start_date', 'completion_date'
        ]
    
    def validate(self, data):
        """Validate application data"""
        program = data.get('program')
        applicant = data.get('applicant', self.context['request'].user)
        
        # Check if program allows applications
        if program and not program.can_apply():
            raise serializers.ValidationError("Applications are not open for this program")
        
        # Check for duplicate application
        if SummerTrainingApplication.objects.filter(program=program, applicant=applicant).exists():
            raise serializers.ValidationError("You have already applied to this program")
        
        return data


class PublicServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for public service requests"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)
    service_code = serializers.CharField(source='service.service_code', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    is_active = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = PublicServiceRequest
        fields = [
            'id', 'service', 'service_title', 'service_code', 'requester',
            'requester_name', 'request_date', 'status', 'request_description',
            'urgency_level', 'preferred_date', 'contact_person',
            'contact_email', 'contact_phone', 'organization',
            'supporting_documents', 'assigned_to', 'assigned_to_name',
            'estimated_completion', 'actual_completion', 'payment_required',
            'payment_amount', 'payment_status', 'payment_date',
            'service_notes', 'results_summary', 'client_feedback',
            'satisfaction_rating', 'is_active', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'service', 'requester', 'request_date', 'assigned_to', 'estimated_completion',
            'actual_completion', 'payment_date'
        ]
    
    def validate(self, data):
        """Validate service request data"""
        service = data.get('service')
        
        # Check if service allows requests
        if service and not service.can_request():
            raise serializers.ValidationError("This service is not currently available for requests")
        
        return data
