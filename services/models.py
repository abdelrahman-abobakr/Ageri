from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel, StatusChoices

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


class TestService(TimeStampedModel):
    """
    Simplified model for test services offered by the organization
    """
    # Basic Information
    name = models.CharField(
        max_length=200,
        help_text="Service name"
    )
    service_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique service identifier (e.g., TS2024-001)"
    )
    description = models.TextField(
        help_text="Full service description"
    )
    category = models.CharField(
        max_length=20,
        choices=ServiceCategory.choices,
        default=ServiceCategory.TESTING
    )

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Base service price"
    )
    is_free = models.BooleanField(
        default=False,
        help_text="Whether this service is free"
    )

    # Service Details
    estimated_duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="Estimated time to complete (e.g., '2-3 business days')"
    )

    # Status and Visibility
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark as featured service"
    )

    # Contact Information
    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for this service"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone for this service"
    )

    # Tags for categorization
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags for categorization"
    )

    # Service Image
    featured_image = models.ImageField(
        upload_to='services/images/',
        blank=True,
        null=True,
        help_text="Main service image"
    )

    class Meta:
        ordering = ['-is_featured', 'name']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['service_code']),
        ]

    def __str__(self):
        return f"{self.service_code} - {self.name}"

    @property
    def is_available(self):
        """Check if service is available"""
        return self.status == StatusChoices.ACTIVE

    @property
    def display_price(self):
        """Return formatted price display"""
        if self.is_free:
            return "Free"
        return f"{self.base_price} EGP"

    @property
    def image_url(self):
        """Return the image URL if available"""
        if self.featured_image:
            return self.featured_image.url
        return None

    @property
    def has_image(self):
        """Check if service has an image"""
        return bool(self.featured_image)

    def clean(self):
        """Model validation"""
        super().clean()
        
        # Ensure service code is uppercase
        if self.service_code:
            self.service_code = self.service_code.upper()
            
        # If marked as free, set price to 0
        if self.is_free:
            self.base_price = Decimal('0.00')
            
        # Validate image file size
        if self.featured_image and self.featured_image.size > 5 * 1024 * 1024:
            raise ValidationError('Image size should not exceed 5MB')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ServiceImage(TimeStampedModel):
    """
    Optional: Simple model for service images (if you need images later)
    """
    service = models.ForeignKey(
        TestService,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='services/images/',
        help_text="Service image"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary image for the service"
    )

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.service.name} - Image {self.id}"

    def clean(self):
        # Validate image file size (5MB limit)
        if self.image and self.image.size > 5 * 1024 * 1024:
            raise ValidationError('Image size should not exceed 5MB')

    def save(self, *args, **kwargs):
        # Ensure only one primary image per service
        if self.is_primary:
            ServiceImage.objects.filter(
                service=self.service,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)