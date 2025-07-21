from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

from core.models import TimeStampedModel, StatusChoices, PriorityChoices

User = get_user_model()


class ServiceCategory(models.TextChoices):
    """Service category choices"""
    TESTING = 'testing', 'Testing & Analysis'
    CONSULTATION = 'consultation', 'Consultation'
    EQUIPMENT_ACCESS = 'equipment_access', 'Equipment Access'
    SAMPLE_ANALYSIS = 'sample_analysis', 'Sample Analysis'
    CALIBRATION = 'calibration', 'Calibration Services'
    TRAINING = 'training', 'Technical Training'
    RESEARCH_SUPPORT = 'research_support', 'Research Support'
    OTHER = 'other', 'Other Services'


class UrgencyLevel(models.TextChoices):
    """Urgency level choices"""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class TestService(TimeStampedModel):
    """
    Model for test services offered by the organization
    """
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(
        max_length=100000,
        blank=True,
        help_text="Brief description for service listings"
        
    )

    # Service Details
    service_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique service identifier (e.g., TS2024-001)"
    )
    category = models.CharField(
        max_length=20,
        choices=ServiceCategory.choices,
        default=ServiceCategory.TESTING
    )

    # Organization
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_services'
    )
    lab = models.ForeignKey(
        'organization.Lab',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_services'
    )

    # Technician Assignment
    technicians = models.ManyToManyField(
        User,
        through='TechnicianAssignment',
        related_name='assigned_services',
        limit_choices_to={'role__in': ['admin', 'moderator']},
        blank=True
    )

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Base service price"
    )
    is_free = models.BooleanField(default=False)
    pricing_structure = models.TextField(
        blank=True,
        help_text="Detailed pricing information (e.g., per sample, per hour)"
    )

    # Service Details
    estimated_duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="Estimated time to complete (e.g., '2-3 business days')"
    )
    sample_requirements = models.TextField(
        blank=True,
        help_text="Sample preparation and requirements"
    )
    equipment_used = models.TextField(
        blank=True,
        help_text="Equipment and instruments used"
    )
    methodology = models.TextField(
        blank=True,
        help_text="Testing methodology and procedures"
    )

    # Capacity and Availability
    max_concurrent_requests = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of concurrent service requests"
    )

    # Requirements
    required_documents = models.TextField(
        blank=True,
        help_text="Documents required for service request"
    )
    safety_requirements = models.TextField(
        blank=True,
        help_text="Safety requirements and precautions"
    )

    # Status and Visibility
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    # Contact Information
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # Media
    featured_image = models.ImageField(
        upload_to='services/test_services/',
        blank=True,
        null=True
    )
    service_brochure = models.FileField(
        upload_to='services/brochures/',
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
        ordering = ['-is_featured', 'name']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['is_featured', 'is_public']),
            models.Index(fields=['department', 'lab']),
        ]

    def __str__(self):
        return f"{self.service_code} - {self.name}"

    @property
    def current_requests(self):
        """Calculate current number of active requests"""
        return self.requests.filter(
            status__in=['submitted', 'under_review', 'approved', 'in_progress']
        ).count()

    @property
    def is_available(self):
        """Check if service is available for requests"""
        return (
            self.status == StatusChoices.ACTIVE and
            self.current_requests < self.max_concurrent_requests
        )

    @property
    def is_at_capacity(self):
        """Check if service is at capacity"""
        return self.current_requests >= self.max_concurrent_requests

    @property
    def availability_percentage(self):
        """Calculate availability percentage"""
        if self.max_concurrent_requests == 0:
            return 0
        return ((self.max_concurrent_requests - self.current_requests) /
                self.max_concurrent_requests) * 100

    def can_be_requested_by(self, user):
        """Check if user can request this service"""
        if not self.is_available:
            return False
        if not self.is_public and user.role == 'researcher':
            return False
        return True


class Client(TimeStampedModel):
    """
    Model for external clients requesting services
    """
    # Basic Information
    name = models.CharField(max_length=200)
    organization = models.CharField(max_length=200, blank=True)
    client_type = models.CharField(
        max_length=20,
        choices=[
            ('individual', 'Individual'),
            ('company', 'Company'),
            ('university', 'University'),
            ('government', 'Government Agency'),
            ('ngo', 'NGO'),
            ('other', 'Other'),
        ],
        default='individual'
    )

    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Professional Information
    position = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Account Information
    client_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique client identifier (e.g., CL2024-001)"
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Billing Information
    billing_address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('net_15', 'Net 15 days'),
            ('net_30', 'Net 30 days'),
            ('net_60', 'Net 60 days'),
        ],
        default='net_30'
    )

    # Notes and History
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the client"
    )

    # Statistics
    total_requests = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['client_type', 'is_active']),
            models.Index(fields=['organization']),
        ]

    def __str__(self):
        if self.organization:
            return f"{self.name} ({self.organization})"
        return self.name

    @property
    def full_contact_info(self):
        """Get formatted contact information"""
        contact = [self.email]
        if self.phone:
            contact.append(self.phone)
        return " | ".join(contact)


class TechnicianAssignment(TimeStampedModel):
    """
    Through model for technician assignments to services
    """
    service = models.ForeignKey(
        TestService,
        on_delete=models.CASCADE,
        related_name='technician_assignments'
    )
    technician = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_assignments',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )

    # Assignment Details
    role = models.CharField(
        max_length=20,
        choices=[
            ('primary', 'Primary Technician'),
            ('secondary', 'Secondary Technician'),
            ('supervisor', 'Supervisor'),
            ('specialist', 'Specialist'),
        ],
        default='primary'
    )

    # Availability
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    # Workload
    max_concurrent_requests = models.PositiveIntegerField(
        default=3,
        help_text="Maximum concurrent requests this technician can handle for this service"
    )

    # Performance
    total_completed = models.PositiveIntegerField(default=0)
    average_completion_time = models.DurationField(null=True, blank=True)

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Notes about this assignment"
    )

    class Meta:
        unique_together = ['service', 'technician']
        ordering = ['service', '-is_active', 'role']

    def __str__(self):
        return f"{self.technician.get_full_name()} - {self.service.name} ({self.role})"

    @property
    def current_requests(self):
        """Calculate current number of active requests assigned to this technician"""
        return ServiceRequest.objects.filter(
            assigned_technician=self.technician,
            service=self.service,
            status__in=['approved', 'in_progress']
        ).count()

    @property
    def is_available(self):
        """Check if technician is available for new requests"""
        return (
            self.is_active and
            self.current_requests < self.max_concurrent_requests and
            (not self.end_date or self.end_date >= timezone.now().date())
        )

    @property
    def workload_percentage(self):
        """Calculate current workload percentage"""
        if self.max_concurrent_requests == 0:
            return 0
        return (self.current_requests / self.max_concurrent_requests) * 100


class ServiceRequest(TimeStampedModel):
    """
    Model for service requests from clients
    """
    # Request Information
    request_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique request identifier (e.g., SR2024-001)"
    )
    service = models.ForeignKey(
        TestService,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='service_requests'
    )

    # Assignment
    assigned_technician = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )

    # Request Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    sample_description = models.TextField(
        blank=True,
        help_text="Description of samples to be tested"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Number of samples or units"
    )

    # Priority and Urgency
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM
    )
    urgency = models.CharField(
        max_length=20,
        choices=UrgencyLevel.choices,
        default=UrgencyLevel.MEDIUM
    )

    # Dates
    requested_date = models.DateTimeField(auto_now_add=True)
    preferred_completion_date = models.DateField(null=True, blank=True)
    started_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
            ('on_hold', 'On Hold'),
        ],
        default='submitted'
    )

    # Pricing
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    final_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    # Files
    request_documents = models.FileField(
        upload_to='services/requests/documents/',
        blank=True,
        null=True,
        help_text="Supporting documents for the request"
    )
    results_file = models.FileField(
        upload_to='services/requests/results/',
        blank=True,
        null=True,
        help_text="Test results and reports"
    )

    # Communication
    client_notes = models.TextField(
        blank=True,
        help_text="Notes from the client"
    )
    internal_notes = models.TextField(
        blank=True,
        help_text="Internal notes for technicians"
    )

    # Review
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_service_requests'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-requested_date']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['service', 'client']),
            models.Index(fields=['assigned_technician']),
            models.Index(fields=['requested_date']),
        ]

    def __str__(self):
        return f"{self.request_id} - {self.title}"

    @property
    def is_overdue(self):
        """Check if request is overdue"""
        if not self.preferred_completion_date:
            return False
        return (
            self.status not in ['completed', 'delivered', 'cancelled'] and
            timezone.now().date() > self.preferred_completion_date
        )

    @property
    def duration_in_progress(self):
        """Calculate how long the request has been in progress"""
        if not self.started_date:
            return None
        end_date = self.completed_date or timezone.now()
        return end_date - self.started_date

    @property
    def total_duration(self):
        """Calculate total duration from request to completion"""
        if not self.completed_date:
            return None
        return self.completed_date - self.requested_date

    def can_be_cancelled(self):
        """Check if request can be cancelled"""
        return self.status in ['submitted', 'under_review', 'approved', 'on_hold']

    def can_be_started(self):
        """Check if request can be started"""
        return self.status == 'approved' and self.assigned_technician

    def can_be_completed(self):
        """Check if request can be completed"""
        return self.status == 'in_progress'
