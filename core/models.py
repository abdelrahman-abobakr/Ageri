from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StatusChoices(models.TextChoices):
    """Common status choices used across the platform"""
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'


class PriorityChoices(models.TextChoices):
    """Priority levels for various content"""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


def upload_to_user_directory(instance, filename):
    """
    Upload files to user-specific directories
    """
    return f'users/{instance.user.id}/{filename}'


def upload_to_documents(instance, filename):
    """
    Upload documents to organized directories
    """
    return f'documents/{instance.__class__.__name__.lower()}/{filename}'
