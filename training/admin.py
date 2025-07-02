from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from .models import (
    Course, SummerTraining, PublicService,
    CourseEnrollment, SummerTrainingApplication, PublicServiceRequest
)


class CourseEnrollmentInline(admin.TabularInline):
    """Inline for course enrollments"""
    model = CourseEnrollment
    extra = 0
    readonly_fields = ['enrollment_date', 'payment_date', 'completion_date']
    fields = [
        'student', 'status', 'payment_status', 'payment_amount',
        'grade', 'attendance_percentage', 'certificate_issued'
    ]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for courses"""
    list_display = [
        'course_code', 'title_short', 'training_type', 'difficulty_level',
        'instructor', 'start_date', 'enrollment_status', 'price', 'status'
    ]
    list_filter = [
        'training_type', 'difficulty_level', 'status', 'is_featured',
        'is_public', 'is_free', 'start_date'
    ]
    search_fields = ['title', 'course_code', 'description', 'tags']
    readonly_fields = ['current_enrollment', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    ordering = ['-is_featured', '-start_date']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'course_code', 'description', 'short_description',
                'training_type', 'difficulty_level'
            )
        }),
        ('Academic Details', {
            'fields': (
                'credits', 'duration_hours', 'prerequisites',
                'materials_provided', 'tags'
            )
        }),
        ('Organization', {
            'fields': ('instructor', 'department')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Capacity & Enrollment', {
            'fields': (
                'max_participants', 'min_participants', 'current_enrollment'
            )
        }),
        ('Pricing', {
            'fields': ('price', 'is_free')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_public')
        }),
        ('Media', {
            'fields': ('featured_image', 'syllabus')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [CourseEnrollmentInline]

    def title_short(self, obj):
        """Display shortened title"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def enrollment_status(self, obj):
        """Display enrollment status with color coding"""
        percentage = obj.enrollment_percentage
        if percentage >= 90:
            color = 'red'
            status = 'Full'
        elif percentage >= 70:
            color = 'orange'
            status = 'High'
        elif percentage >= 30:
            color = 'green'
            status = 'Good'
        else:
            color = 'gray'
            status = 'Low'

        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.current_enrollment,
            obj.max_participants,
            int(percentage)
        )
    enrollment_status.short_description = 'Enrollment'

    actions = ['mark_as_published', 'mark_as_draft', 'mark_as_featured']

    def mark_as_published(self, request, queryset):
        """Mark selected courses as published"""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} courses marked as published.')
    mark_as_published.short_description = 'Mark selected courses as published'

    def mark_as_draft(self, request, queryset):
        """Mark selected courses as draft"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} courses marked as draft.')
    mark_as_draft.short_description = 'Mark selected courses as draft'

    def mark_as_featured(self, request, queryset):
        """Mark selected courses as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} courses marked as featured.')
    mark_as_featured.short_description = 'Mark selected courses as featured'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'instructor', 'department'
        )


class SummerTrainingApplicationInline(admin.TabularInline):
    """Inline for summer training applications"""
    model = SummerTrainingApplication
    extra = 0
    readonly_fields = ['application_date', 'review_date']
    fields = [
        'applicant', 'status', 'university', 'major', 'year_of_study',
        'gpa', 'reviewed_by'
    ]


@admin.register(SummerTraining)
class SummerTrainingAdmin(admin.ModelAdmin):
    """Admin interface for summer training programs"""
    list_display = [
        'program_code', 'title_short', 'supervisor', 'start_date',
        'duration_weeks', 'enrollment_status', 'is_paid', 'status'
    ]
    list_filter = [
        'difficulty_level', 'status', 'is_featured', 'is_public',
        'is_paid', 'provides_certificate', 'start_date'
    ]
    search_fields = ['title', 'program_code', 'description', 'tags']
    readonly_fields = ['current_enrollment', 'total_hours', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    ordering = ['-is_featured', '-start_date']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'program_code', 'description', 'short_description',
                'difficulty_level'
            )
        }),
        ('Program Details', {
            'fields': (
                'duration_weeks', 'hours_per_week', 'total_hours',
                'learning_objectives', 'project_description', 'tags'
            )
        }),
        ('Organization', {
            'fields': ('supervisor', 'department', 'lab')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'application_deadline')
        }),
        ('Capacity & Enrollment', {
            'fields': (
                'max_trainees', 'min_trainees', 'current_enrollment'
            )
        }),
        ('Requirements', {
            'fields': ('academic_requirements', 'skills_requirements')
        }),
        ('Compensation & Benefits', {
            'fields': (
                'is_paid', 'stipend_amount', 'provides_certificate',
                'provides_recommendation'
            )
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_public')
        }),
        ('Media', {
            'fields': ('featured_image', 'program_brochure')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [SummerTrainingApplicationInline]

    def title_short(self, obj):
        """Display shortened title"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def enrollment_status(self, obj):
        """Display enrollment status with color coding"""
        percentage = (obj.current_enrollment / obj.max_trainees) * 100 if obj.max_trainees > 0 else 0
        if percentage >= 90:
            color = 'red'
            status = 'Full'
        elif percentage >= 70:
            color = 'orange'
            status = 'High'
        elif percentage >= 30:
            color = 'green'
            status = 'Good'
        else:
            color = 'gray'
            status = 'Low'

        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.current_enrollment,
            obj.max_trainees,
            int(percentage)
        )
    enrollment_status.short_description = 'Applications'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'supervisor', 'department', 'lab'
        )


class PublicServiceRequestInline(admin.TabularInline):
    """Inline for public service requests"""
    model = PublicServiceRequest
    extra = 0
    readonly_fields = ['request_date', 'actual_completion']
    fields = [
        'requester', 'status', 'urgency_level', 'assigned_to',
        'estimated_completion', 'payment_required'
    ]


@admin.register(PublicService)
class PublicServiceAdmin(admin.ModelAdmin):
    """Admin interface for public services"""
    list_display = [
        'service_code', 'title_short', 'service_category', 'coordinator',
        'is_ongoing', 'request_status', 'is_free', 'status'
    ]
    list_filter = [
        'service_category', 'status', 'is_featured', 'is_public',
        'is_ongoing', 'is_free'
    ]
    search_fields = ['title', 'service_code', 'description', 'tags']
    readonly_fields = ['current_requests', 'created_at', 'updated_at']
    ordering = ['-is_featured', 'title']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'service_code', 'description', 'short_description',
                'service_category'
            )
        }),
        ('Organization', {
            'fields': ('coordinator', 'department')
        }),
        ('Availability', {
            'fields': ('is_ongoing', 'start_date', 'end_date')
        }),
        ('Capacity', {
            'fields': ('max_concurrent_requests', 'current_requests')
        }),
        ('Pricing', {
            'fields': ('is_free', 'base_price', 'pricing_details')
        }),
        ('Requirements & Process', {
            'fields': (
                'eligibility_criteria', 'required_documents',
                'process_description', 'estimated_turnaround'
            )
        }),
        ('Contact & Location', {
            'fields': ('contact_email', 'contact_phone', 'location')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_public')
        }),
        ('Media', {
            'fields': ('featured_image', 'service_brochure', 'tags')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [PublicServiceRequestInline]

    def title_short(self, obj):
        """Display shortened title"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def request_status(self, obj):
        """Display request status with color coding"""
        percentage = (obj.current_requests / obj.max_concurrent_requests) * 100 if obj.max_concurrent_requests > 0 else 0
        if percentage >= 90:
            color = 'red'
            status = 'At Capacity'
        elif percentage >= 70:
            color = 'orange'
            status = 'High Load'
        elif percentage >= 30:
            color = 'green'
            status = 'Available'
        else:
            color = 'gray'
            status = 'Low Usage'

        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.current_requests,
            obj.max_concurrent_requests,
            int(percentage)
        )
    request_status.short_description = 'Requests'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'coordinator', 'department'
        )


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for course enrollments"""
    list_display = [
        'student_name', 'course_title', 'status', 'payment_status',
        'enrollment_date', 'grade', 'certificate_issued'
    ]
    list_filter = [
        'status', 'payment_status', 'certificate_issued',
        'enrollment_date', 'course__training_type'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 'student__email',
        'course__title', 'course__course_code'
    ]
    readonly_fields = ['enrollment_date', 'payment_date', 'completion_date']
    date_hierarchy = 'enrollment_date'
    ordering = ['-enrollment_date']

    fieldsets = (
        ('Enrollment Information', {
            'fields': ('course', 'student', 'enrollment_date', 'status')
        }),
        ('Payment Information', {
            'fields': (
                'payment_status', 'payment_amount', 'payment_date',
                'payment_reference'
            )
        }),
        ('Academic Information', {
            'fields': ('grade', 'attendance_percentage')
        }),
        ('Completion', {
            'fields': (
                'completion_date', 'certificate_issued', 'certificate_number'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        })
    )

    def student_name(self, obj):
        """Display student name"""
        return obj.student.get_full_name()
    student_name.short_description = 'Student'

    def course_title(self, obj):
        """Display course title"""
        return obj.course.title[:40] + '...' if len(obj.course.title) > 40 else obj.course.title
    course_title.short_description = 'Course'

    actions = ['mark_as_completed', 'issue_certificates']

    def mark_as_completed(self, request, queryset):
        """Mark selected enrollments as completed"""
        for enrollment in queryset:
            enrollment.mark_completed()
        self.message_user(request, f'{queryset.count()} enrollments marked as completed.')
    mark_as_completed.short_description = 'Mark selected enrollments as completed'

    def issue_certificates(self, request, queryset):
        """Issue certificates for completed enrollments"""
        updated = queryset.filter(status='completed').update(certificate_issued=True)
        self.message_user(request, f'{updated} certificates issued.')
    issue_certificates.short_description = 'Issue certificates for completed enrollments'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'course'
        )


@admin.register(SummerTrainingApplication)
class SummerTrainingApplicationAdmin(admin.ModelAdmin):
    """Admin interface for summer training applications"""
    list_display = [
        'applicant_name', 'program_title', 'status', 'university',
        'year_of_study', 'gpa', 'application_date'
    ]
    list_filter = [
        'status', 'year_of_study', 'application_date',
        'program__difficulty_level', 'certificate_issued'
    ]
    search_fields = [
        'applicant__first_name', 'applicant__last_name', 'applicant__email',
        'program__title', 'program__program_code', 'university', 'major'
    ]
    readonly_fields = ['application_date', 'review_date']
    date_hierarchy = 'application_date'
    ordering = ['-application_date']

    fieldsets = (
        ('Application Information', {
            'fields': ('program', 'applicant', 'application_date', 'status')
        }),
        ('Academic Information', {
            'fields': ('university', 'major', 'year_of_study', 'gpa')
        }),
        ('Application Materials', {
            'fields': (
                'motivation_letter', 'relevant_experience',
                'skills_and_interests'
            )
        }),
        ('Documents', {
            'fields': ('cv_file', 'transcript', 'recommendation_letter')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'review_date', 'review_notes')
        }),
        ('Completion', {
            'fields': (
                'start_date', 'completion_date', 'final_evaluation',
                'certificate_issued'
            )
        })
    )

    def applicant_name(self, obj):
        """Display applicant name"""
        return obj.applicant.get_full_name()
    applicant_name.short_description = 'Applicant'

    def program_title(self, obj):
        """Display program title"""
        return obj.program.title[:40] + '...' if len(obj.program.title) > 40 else obj.program.title
    program_title.short_description = 'Program'

    actions = ['approve_applications', 'reject_applications', 'mark_under_review']

    def approve_applications(self, request, queryset):
        """Approve selected applications"""
        updated = queryset.update(status='approved', reviewed_by=request.user, review_date=timezone.now())
        self.message_user(request, f'{updated} applications approved.')
    approve_applications.short_description = 'Approve selected applications'

    def reject_applications(self, request, queryset):
        """Reject selected applications"""
        updated = queryset.update(status='rejected', reviewed_by=request.user, review_date=timezone.now())
        self.message_user(request, f'{updated} applications rejected.')
    reject_applications.short_description = 'Reject selected applications'

    def mark_under_review(self, request, queryset):
        """Mark selected applications as under review"""
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} applications marked as under review.')
    mark_under_review.short_description = 'Mark selected applications as under review'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'applicant', 'program', 'reviewed_by'
        )


@admin.register(PublicServiceRequest)
class PublicServiceRequestAdmin(admin.ModelAdmin):
    """Admin interface for public service requests"""
    list_display = [
        'requester_name', 'service_title', 'status', 'urgency_level',
        'request_date', 'assigned_to', 'is_overdue'
    ]
    list_filter = [
        'status', 'urgency_level', 'payment_required', 'payment_status',
        'request_date', 'service__service_category'
    ]
    search_fields = [
        'requester__first_name', 'requester__last_name', 'requester__email',
        'service__title', 'service__service_code', 'contact_person',
        'organization'
    ]
    readonly_fields = ['request_date', 'payment_date', 'is_overdue']
    date_hierarchy = 'request_date'
    ordering = ['-request_date']

    fieldsets = (
        ('Request Information', {
            'fields': (
                'service', 'requester', 'request_date', 'status',
                'request_description', 'urgency_level', 'preferred_date'
            )
        }),
        ('Contact Information', {
            'fields': (
                'contact_person', 'contact_email', 'contact_phone',
                'organization'
            )
        }),
        ('Documents', {
            'fields': ('supporting_documents',)
        }),
        ('Processing', {
            'fields': (
                'assigned_to', 'estimated_completion', 'actual_completion'
            )
        }),
        ('Payment', {
            'fields': (
                'payment_required', 'payment_amount', 'payment_status',
                'payment_date'
            )
        }),
        ('Results & Feedback', {
            'fields': (
                'service_notes', 'results_summary', 'client_feedback',
                'satisfaction_rating'
            )
        })
    )

    def requester_name(self, obj):
        """Display requester name"""
        return obj.requester.get_full_name()
    requester_name.short_description = 'Requester'

    def service_title(self, obj):
        """Display service title"""
        return obj.service.title[:40] + '...' if len(obj.service.title) > 40 else obj.service.title
    service_title.short_description = 'Service'

    def is_overdue(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_overdue.short_description = 'Overdue'

    actions = ['approve_requests', 'mark_in_progress', 'mark_completed']

    def approve_requests(self, request, queryset):
        """Approve selected requests"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} requests approved.')
    approve_requests.short_description = 'Approve selected requests'

    def mark_in_progress(self, request, queryset):
        """Mark selected requests as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} requests marked as in progress.')
    mark_in_progress.short_description = 'Mark selected requests as in progress'

    def mark_completed(self, request, queryset):
        """Mark selected requests as completed"""
        for req in queryset:
            req.mark_completed()
        self.message_user(request, f'{queryset.count()} requests marked as completed.')
    mark_completed.short_description = 'Mark selected requests as completed'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'requester', 'service', 'assigned_to'
        )
