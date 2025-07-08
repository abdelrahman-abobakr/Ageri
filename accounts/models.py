from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import FileExtensionValidator
from core.models import TimeStampedModel, StatusChoices, upload_to_user_directory


class UserRole(models.TextChoices):
    """User role choices"""
    ADMIN = 'admin', 'Admin'
    MODERATOR = 'moderator', 'Moderator'
    RESEARCHER = 'researcher', 'Researcher'


class CustomUserManager(UserManager):
    """Custom user manager to handle superuser creation"""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', UserRole.ADMIN)
        extra_fields.setdefault('is_approved', True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with role-based permissions
    """
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.RESEARCHER
    )
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_users'
    )

    # Additional fields
    phone = models.CharField(max_length=20, blank=True)
    institution = models.CharField(max_length=200, blank=True)

    # Custom manager
    objects = CustomUserManager()
    department = models.CharField(max_length=200, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    @property
    def is_researcher(self):
        return self.role == UserRole.RESEARCHER

    def can_approve_users(self):
        return self.is_admin

    def can_create_content(self):
        return self.is_admin or self.is_moderator

    def save(self, *args, **kwargs):
        # Automatically set is_staff for admin users
        if self.role == UserRole.ADMIN:
            self.is_staff = True
        # Auto-approve superusers
        if self.is_superuser and not self.is_approved:
            self.is_approved = True
        super().save(*args, **kwargs)


class UserProfile(TimeStampedModel):
    """
    Extended user profile for researchers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Professional Information
    orcid_id = models.CharField(max_length=19, blank=True, help_text="ORCID ID (e.g., 0000-0000-0000-0000)")
    bio = models.TextField(blank=True, max_length=1000)
    research_interests = models.TextField(blank=True, max_length=500)

    # CV and Documents
    cv_file = models.FileField(
        upload_to=upload_to_user_directory,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text="Upload CV (PDF, DOC, DOCX only)"
    )

    # Social Links
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    google_scholar = models.URLField(blank=True)
    researchgate = models.URLField(blank=True)

    # Admin Notes
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin use")

    # Profile Status
    is_public = models.BooleanField(default=True, help_text="Make profile visible to public")

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    @property
    def has_cv(self):
        return bool(self.cv_file)

    @property
    def has_orcid(self):
        return bool(self.orcid_id)
