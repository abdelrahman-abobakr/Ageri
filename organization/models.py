from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, StatusChoices


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
        return self.researchers.filter(status=StatusChoices.ACTIVE).count()

    @property
    def is_at_capacity(self):
        return self.current_researchers_count >= self.capacity

    @property
    def available_spots(self):
        return max(0, self.capacity - self.current_researchers_count)


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
