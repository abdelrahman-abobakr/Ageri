from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from core.models import TimeStampedModel, StatusChoices


def upload_to_organization(instance, filename):
    """Upload organization files to organized directories"""
    return f'organization/{filename}'


class Department(TimeStampedModel):
    """
    Department model for organizing research units
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )

    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_labs(self):
        return self.labs.count()

    @property
    def total_researchers(self):
        return self.researchers.count()


class Lab(TimeStampedModel):
    """
    Laboratory model within departments
    """
    name = models.CharField(max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='labs'
    )
    description = models.TextField(blank=True)

    # Lab Head
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_labs',
        limit_choices_to={'role__in': ['admin', 'moderator', 'researcher']}
    )

    # Equipment and Resources
    equipment = models.TextField(blank=True, help_text="List of available equipment")
    capacity = models.PositiveIntegerField(default=10, help_text="Maximum number of researchers")

    # Contact Information
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )

    class Meta:
        verbose_name = 'Laboratory'
        verbose_name_plural = 'Laboratories'
        ordering = ['department__name', 'name']
        unique_together = ['name', 'department']

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    @property
    def current_researchers_count(self):
        return self.researcher_assignments.filter(status=StatusChoices.ACTIVE).count()

    @property
    def is_at_capacity(self):
        return self.current_researchers_count >= self.capacity

    @property
    def available_spots(self):
        return max(0, self.capacity - self.current_researchers_count)

    @property
    def is_full(self):
        return self.current_researchers_count >= self.capacity


class ResearcherAssignment(TimeStampedModel):
    """
    Through model for researcher-lab assignments with additional metadata
    """
    researcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_assignments',
        limit_choices_to={'role': 'researcher'}
    )
    lab = models.ForeignKey(
        Lab,
        on_delete=models.CASCADE,
        related_name='researcher_assignments'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='researcher_assignments'
    )

    # Assignment Details
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Position/role in the lab (e.g., PhD Student, Postdoc, Research Assistant)"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )

    # Assignment metadata
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='made_assignments',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )
    notes = models.TextField(blank=True, help_text="Additional notes about the assignment")

    class Meta:
        verbose_name = 'Researcher Assignment'
        verbose_name_plural = 'Researcher Assignments'
        ordering = ['-start_date']
        unique_together = ['researcher', 'lab', 'start_date']

    def __str__(self):
        return f"{self.researcher.get_full_name()} → {self.lab.name}"

    @property
    def is_active(self):
        return self.status == StatusChoices.ACTIVE

    @property
    def duration_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None

    def clean(self):
        from django.core.exceptions import ValidationError

        # Ensure end_date is after start_date
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")

        # Ensure department matches lab's department
        if self.lab and self.department != self.lab.department:
            raise ValidationError("Department must match the lab's department")


# Add the many-to-many relationship to the User model through signals
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def add_researcher_relationships(sender, **kwargs):
    """
    Add many-to-many relationships to User model after migration
    """
    if sender.name == 'organization':
        from accounts.models import User

        # Add labs relationship to User model if it doesn't exist
        if not hasattr(User, 'labs'):
            User.add_to_class(
                'labs',
                models.ManyToManyField(
                    Lab,
                    through=ResearcherAssignment,
                    through_fields=('researcher', 'lab'),
                    related_name='researchers',
                    blank=True
                )
            )

        # Add departments relationship to User model if it doesn't exist
        if not hasattr(User, 'departments'):
            User.add_to_class(
                'departments',
                models.ManyToManyField(
                    Department,
                    through=ResearcherAssignment,
                    through_fields=('researcher', 'department'),
                    related_name='researchers',
                    blank=True
                )
            )


class OrganizationSettings(TimeStampedModel):
    """
    Singleton model for organization-wide settings and content
    """
    # Organization Identity
    name = models.CharField(
        max_length=200,
        default="Scientific Research Organization",
        help_text="Organization name"
    )

    # Vision and Mission
    vision = models.TextField(
        blank=True,
        help_text="Organization vision statement"
    )
    vision_image = models.ImageField(
        upload_to=upload_to_organization,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Vision statement image (JPG, PNG)"
    )

    mission = models.TextField(
        blank=True,
        help_text="Organization mission statement"
    )
    mission_image = models.ImageField(
        upload_to=upload_to_organization,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Mission statement image (JPG, PNG)"
    )

    # About and Description
    about = models.TextField(
        blank=True,
        help_text="About the organization"
    )

    # Contact Information
    email = models.EmailField(blank=True, help_text="Main contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Main contact phone")
    address = models.TextField(blank=True, help_text="Organization address")

    # Social Media
    website = models.URLField(blank=True, help_text="Official website URL")
    facebook = models.URLField(blank=True, help_text="Facebook page URL")
    twitter = models.URLField(blank=True, help_text="Twitter profile URL")
    linkedin = models.URLField(blank=True, help_text="LinkedIn page URL")
    instagram = models.URLField(blank=True, help_text="Instagram profile URL")

    # Media Files
    logo = models.ImageField(
        upload_to=upload_to_organization,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])],
        help_text="Organization logo (JPG, PNG, SVG)"
    )
    banner = models.ImageField(
        upload_to=upload_to_organization,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Organization banner image (JPG, PNG)"
    )

    # Additional Settings
    enable_registration = models.BooleanField(
        default=True,
        help_text="Allow new user registration"
    )
    require_approval = models.BooleanField(
        default=True,
        help_text="Require admin approval for new users"
    )
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Enable maintenance mode"
    )
    maintenance_message = models.TextField(
        blank=True,
        help_text="Message to display during maintenance"
    )

    class Meta:
        verbose_name = 'Organization Settings'
        verbose_name_plural = 'Organization Settings'

    def __str__(self):
        return f"Settings for {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and OrganizationSettings.objects.exists():
            raise ValueError("Only one OrganizationSettings instance is allowed")
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
