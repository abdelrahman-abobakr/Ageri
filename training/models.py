from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

from core.models import TimeStampedModel, StatusChoices, PriorityChoices

User = get_user_model()


class TrainingType(models.TextChoices):
    """Training type choices"""
    COURSE = 'course', 'Course'
    SUMMER_TRAINING = 'summer_training', 'Summer Training'
    PUBLIC_SERVICE = 'public_service', 'Public Service'
    WORKSHOP = 'workshop', 'Workshop'
    SEMINAR = 'seminar', 'Seminar'


class DifficultyLevel(models.TextChoices):
    """Difficulty level choices"""
    BEGINNER = 'beginner', 'Beginner'
    INTERMEDIATE = 'intermediate', 'Intermediate'
    ADVANCED = 'advanced', 'Advanced'
    EXPERT = 'expert', 'Expert'


class PaymentStatus(models.TextChoices):
    """Payment status choices"""
    PENDING = 'pending', 'Pending'
    PAID = 'paid', 'Paid'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class Course(TimeStampedModel):
    """
    Model for training courses
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief description for course listings"
    )

    # Course details
    course_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique course identifier (e.g., CS101)"
    )
    credits = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    duration_hours = models.PositiveIntegerField(
        help_text="Total course duration in hours"
    )

    # Classification
    training_type = models.CharField(
        max_length=20,
        choices=TrainingType.choices,
        default=TrainingType.COURSE
    )
    difficulty_level = models.CharField(
        max_length=15,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )

    # Instructor and organization
    instructor = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the course instructor"
    )
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    # Scheduling
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField()

    # Capacity and enrollment
    max_participants = models.PositiveIntegerField(default=30)
    min_participants = models.PositiveIntegerField(default=5)
    current_enrollment = models.PositiveIntegerField(default=0)

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_free = models.BooleanField(default=False)

    # Status and visibility
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT
    )
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    # Requirements and materials
    prerequisites = models.TextField(
        blank=True,
        help_text="Course prerequisites and requirements"
    )
    materials_provided = models.TextField(
        blank=True,
        help_text="Materials and resources provided"
    )

    # Media
    featured_image = models.ImageField(
        upload_to='training/courses/',
        blank=True,
        null=True
    )
    syllabus = models.FileField(
        upload_to='training/syllabi/',
        blank=True,
        null=True,
        help_text="Course syllabus PDF"
    )

    # Metadata
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags for categorization"
    )

    class Meta:
        ordering = ['-is_featured', '-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['training_type', 'difficulty_level']),
            models.Index(fields=['is_featured', 'is_public']),
        ]

    def __str__(self):
        return f"{self.course_code} - {self.title}"

    def clean(self):
        """Validate course data"""
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("End date must be after start date")

        if self.registration_deadline and self.start_date:
            if self.registration_deadline >= self.start_date:
                raise ValidationError("Registration deadline must be before start date")

        if self.min_participants > self.max_participants:
            raise ValidationError("Minimum participants cannot exceed maximum participants")

    @property
    def is_registration_open(self):
        """Check if registration is still open"""
        return (
            self.status == StatusChoices.PUBLISHED and
            timezone.now().date() <= self.registration_deadline
        )

    @property
    def is_full(self):
        """Check if course is at capacity"""
        return self.current_enrollment >= self.max_participants

    @property
    def enrollment_percentage(self):
        """Calculate enrollment percentage"""
        if self.max_participants == 0:
            return 0
        return (self.current_enrollment / self.max_participants) * 100

    def can_register(self):
        """Check if new registrations are allowed"""
        return (
            self.is_registration_open and
            not self.is_full and
            self.status == StatusChoices.PUBLISHED
        )


class SummerTraining(TimeStampedModel):
    """
    Model for summer training programs
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief description for program listings"
    )

    # Program details
    program_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique program identifier (e.g., ST2024-01)"
    )
    duration_weeks = models.PositiveIntegerField(
        default=8,
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Program duration in weeks"
    )
    hours_per_week = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(10), MaxValueValidator(60)],
        help_text="Training hours per week"
    )

    # Classification
    training_type = models.CharField(
        max_length=20,
        choices=TrainingType.choices,
        default=TrainingType.SUMMER_TRAINING
    )
    difficulty_level = models.CharField(
        max_length=15,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.INTERMEDIATE
    )

    # Supervision and organization
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_summer_trainings',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='summer_trainings'
    )
    lab = models.ForeignKey(
        'organization.Lab',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='summer_trainings'
    )

    # Scheduling
    start_date = models.DateField()
    end_date = models.DateField()
    application_deadline = models.DateField()

    # Capacity and enrollment
    max_trainees = models.PositiveIntegerField(default=10)
    min_trainees = models.PositiveIntegerField(default=3)
    current_enrollment = models.PositiveIntegerField(default=0)

    # Requirements
    academic_requirements = models.TextField(
        help_text="Academic requirements (e.g., minimum GPA, year of study)"
    )
    skills_requirements = models.TextField(
        blank=True,
        help_text="Required skills and knowledge"
    )

    # Program details
    learning_objectives = models.TextField(
        help_text="What trainees will learn and achieve"
    )
    project_description = models.TextField(
        blank=True,
        help_text="Description of projects trainees will work on"
    )

    # Compensation and benefits
    is_paid = models.BooleanField(default=False)
    stipend_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monthly stipend amount"
    )
    provides_certificate = models.BooleanField(default=True)
    provides_recommendation = models.BooleanField(default=True)

    # Status and visibility
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT
    )
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    # Media
    featured_image = models.ImageField(
        upload_to='training/summer_programs/',
        blank=True,
        null=True
    )
    program_brochure = models.FileField(
        upload_to='training/brochures/',
        blank=True,
        null=True,
        help_text="Program brochure PDF"
    )

    # Metadata
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags for categorization"
    )

    class Meta:
        ordering = ['-is_featured', '-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['is_featured', 'is_public']),
            models.Index(fields=['application_deadline']),
        ]

    def __str__(self):
        return f"{self.program_code} - {self.title}"

    def clean(self):
        """Validate summer training data"""
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("End date must be after start date")

        if self.application_deadline and self.start_date:
            if self.application_deadline >= self.start_date:
                raise ValidationError("Application deadline must be before start date")

        if self.min_trainees > self.max_trainees:
            raise ValidationError("Minimum trainees cannot exceed maximum trainees")

    @property
    def is_application_open(self):
        """Check if applications are still open"""
        return (
            self.status == StatusChoices.PUBLISHED and
            timezone.now().date() <= self.application_deadline
        )

    @property
    def is_full(self):
        """Check if program is at capacity"""
        return self.current_enrollment >= self.max_trainees

    @property
    def total_hours(self):
        """Calculate total training hours"""
        return self.duration_weeks * self.hours_per_week

    def can_apply(self):
        """Check if new applications are allowed"""
        return (
            self.is_application_open and
            not self.is_full and
            self.status == StatusChoices.PUBLISHED
        )


class PublicService(TimeStampedModel):
    """
    Model for public service programs
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief description for service listings"
    )

    # Service details
    service_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique service identifier (e.g., PS2024-01)"
    )
    service_category = models.CharField(
        max_length=50,
        choices=[
            ('consultation', 'Consultation'),
            ('testing', 'Testing & Analysis'),
            ('training', 'Training & Workshops'),
            ('research', 'Research Collaboration'),
            ('equipment', 'Equipment Access'),
            ('other', 'Other Services'),
        ],
        default='consultation'
    )

    # Organization
    coordinator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_public_services',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='public_services'
    )

    # Availability
    is_ongoing = models.BooleanField(
        default=True,
        help_text="Whether this service is continuously available"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date for time-limited services"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date for time-limited services"
    )

    # Capacity
    max_concurrent_requests = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of concurrent service requests"
    )
    current_requests = models.PositiveIntegerField(default=0)

    # Pricing
    is_free = models.BooleanField(default=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Base service price"
    )
    pricing_details = models.TextField(
        blank=True,
        help_text="Detailed pricing information and structure"
    )

    # Requirements and process
    eligibility_criteria = models.TextField(
        blank=True,
        help_text="Who can access this service"
    )
    required_documents = models.TextField(
        blank=True,
        help_text="Documents required for service request"
    )
    process_description = models.TextField(
        help_text="How to request and receive this service"
    )
    estimated_turnaround = models.CharField(
        max_length=100,
        blank=True,
        help_text="Estimated time to complete service (e.g., '2-3 business days')"
    )

    # Status and visibility
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PUBLISHED
    )
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    # Contact and location
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Physical location where service is provided"
    )

    # Media
    featured_image = models.ImageField(
        upload_to='training/public_services/',
        blank=True,
        null=True
    )
    service_brochure = models.FileField(
        upload_to='training/service_brochures/',
        blank=True,
        null=True,
        help_text="Service information brochure"
    )

    # Metadata
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags for categorization"
    )

    class Meta:
        ordering = ['-is_featured', 'title']
        indexes = [
            models.Index(fields=['status', 'service_category']),
            models.Index(fields=['is_featured', 'is_public']),
            models.Index(fields=['is_ongoing']),
        ]

    def __str__(self):
        return f"{self.service_code} - {self.title}"

    def clean(self):
        """Validate public service data"""
        from django.core.exceptions import ValidationError

        if not self.is_ongoing:
            if not self.start_date or not self.end_date:
                raise ValidationError("Start and end dates are required for time-limited services")

            if self.start_date >= self.end_date:
                raise ValidationError("End date must be after start date")

    @property
    def is_available(self):
        """Check if service is currently available"""
        if not self.status == StatusChoices.PUBLISHED:
            return False

        if self.is_ongoing:
            return True

        if self.start_date and self.end_date:
            today = timezone.now().date()
            return self.start_date <= today <= self.end_date

        return False

    @property
    def is_at_capacity(self):
        """Check if service is at capacity"""
        return self.current_requests >= self.max_concurrent_requests

    def can_request(self):
        """Check if new service requests are allowed"""
        return self.is_available and not self.is_at_capacity


class CourseEnrollment(TimeStampedModel):
    """
    Model for course enrollments
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )

    # Enrollment details
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
            ('dropped', 'Dropped'),
        ],
        default='pending'
    )

    # Payment information
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    # Academic information
    grade = models.CharField(
        max_length=5,
        blank=True,
        help_text="Final grade (A, B, C, D, F)"
    )
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Completion
    completion_date = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=50, blank=True)

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the enrollment"
    )

    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-enrollment_date']
        indexes = [
            models.Index(fields=['status', 'enrollment_date']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"

    @property
    def is_active(self):
        """Check if enrollment is active"""
        return self.status in ['approved', 'completed']

    def mark_completed(self):
        """Mark enrollment as completed"""
        self.status = 'completed'
        self.completion_date = timezone.now()
        self.save(update_fields=['status', 'completion_date'])


class SummerTrainingApplication(TimeStampedModel):
    """
    Model for summer training applications
    """
    program = models.ForeignKey(
        SummerTraining,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='summer_training_applications'
    )

    # Application details
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
            ('withdrawn', 'Withdrawn'),
        ],
        default='submitted'
    )

    # Academic information
    university = models.CharField(max_length=200)
    major = models.CharField(max_length=100)
    year_of_study = models.CharField(
        max_length=20,
        choices=[
            ('freshman', 'Freshman'),
            ('sophomore', 'Sophomore'),
            ('junior', 'Junior'),
            ('senior', 'Senior'),
            ('graduate', 'Graduate'),
        ]
    )
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(4)]
    )

    # Application materials
    motivation_letter = models.TextField(
        help_text="Why do you want to join this program?"
    )
    relevant_experience = models.TextField(
        blank=True,
        help_text="Relevant academic or professional experience"
    )
    skills_and_interests = models.TextField(
        help_text="Technical skills and research interests"
    )

    # Documents
    cv_file = models.FileField(
        upload_to='training/applications/cvs/',
        blank=True,
        null=True,
        help_text="Upload your CV/Resume (optional)"
    )
    transcript = models.FileField(
        upload_to='training/applications/transcripts/',
        blank=True,
        null=True,
        help_text="Academic transcript (optional)"
    )
    recommendation_letter = models.FileField(
        upload_to='training/applications/recommendations/',
        blank=True,
        null=True,
        help_text="Letter of recommendation (optional)"
    )

    # Review information
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_summer_applications'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # Completion
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    final_evaluation = models.TextField(blank=True)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = ['program', 'applicant']
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['status', 'application_date']),
            models.Index(fields=['program', 'status']),
        ]

    def __str__(self):
        return f"{self.applicant.get_full_name()} - {self.program.title}"

    @property
    def is_active(self):
        """Check if application is active"""
        return self.status in ['approved', 'completed']


class PublicServiceRequest(TimeStampedModel):
    """
    Model for public service requests
    """
    service = models.ForeignKey(
        PublicService,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_requests'
    )

    # Request details
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='submitted'
    )

    # Request information
    request_description = models.TextField(
        help_text="Detailed description of what you need"
    )
    urgency_level = models.CharField(
        max_length=10,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM
    )
    preferred_date = models.DateField(
        null=True,
        blank=True,
        help_text="Preferred date for service delivery"
    )

    # Contact information
    contact_person = models.CharField(
        max_length=100,
        help_text="Primary contact person for this request"
    )
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organization or institution making the request"
    )

    # Documents and attachments
    supporting_documents = models.FileField(
        upload_to='training/service_requests/',
        blank=True,
        null=True,
        help_text="Supporting documents for the request"
    )

    # Processing information
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_service_requests',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )
    estimated_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)

    # Payment information
    payment_required = models.BooleanField(default=False)
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_date = models.DateTimeField(null=True, blank=True)

    # Results and feedback
    service_notes = models.TextField(
        blank=True,
        help_text="Internal notes about service delivery"
    )
    results_summary = models.TextField(
        blank=True,
        help_text="Summary of service results"
    )
    client_feedback = models.TextField(
        blank=True,
        help_text="Client feedback about the service"
    )
    satisfaction_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Client satisfaction rating (1-5)"
    )

    class Meta:
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['status', 'request_date']),
            models.Index(fields=['service', 'status']),
            models.Index(fields=['urgency_level']),
        ]

    def __str__(self):
        return f"{self.requester.get_full_name()} - {self.service.title}"

    @property
    def is_active(self):
        """Check if request is active"""
        return self.status in ['approved', 'in_progress']

    @property
    def is_overdue(self):
        """Check if request is overdue"""
        if self.estimated_completion and self.status not in ['completed', 'cancelled', 'rejected']:
            return timezone.now().date() > self.estimated_completion
        return False

    def mark_completed(self):
        """Mark request as completed"""
        self.status = 'completed'
        self.actual_completion = timezone.now().date()
        self.save(update_fields=['status', 'actual_completion'])
