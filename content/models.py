from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from core.models import TimeStampedModel, StatusChoices, PriorityChoices, upload_to_documents

User = get_user_model()


class AnnouncementType(models.TextChoices):
    """Types of announcements"""
    GENERAL = 'general', 'General'
    URGENT = 'urgent', 'Urgent'
    MAINTENANCE = 'maintenance', 'Maintenance'
    EVENT = 'event', 'Event'
    DEADLINE = 'deadline', 'Deadline'
    NEWS = 'news', 'News'
    POLICY = 'policy', 'Policy Update'


class TargetAudience(models.TextChoices):
    """Target audience for announcements"""
    ALL = 'all', 'All Users'
    RESEARCHERS = 'researchers', 'Researchers Only'
    MODERATORS = 'moderators', 'Moderators Only'
    ADMINS = 'admins', 'Admins Only'
    APPROVED_USERS = 'approved', 'Approved Users Only'


def upload_to_announcements(instance, filename):
    """Upload announcement attachments to organized directories"""
    return f'content/announcements/{instance.announcement.id}/{filename}'

def upload_to_announcement_images(instance, filename):
    """Upload announcement images to organized directories"""
    return f'content/announcements/{instance.announcement.id}/images/{filename}'


class Announcement(TimeStampedModel):
    """
    Model for system-wide announcements
    """
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Main announcement content")
    summary = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief summary for list views (auto-generated if empty)"
    )

    # Classification
    announcement_type = models.CharField(
        max_length=20,
        choices=AnnouncementType.choices,
        default=AnnouncementType.GENERAL
    )
    priority = models.CharField(
        max_length=10,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM
    )

    # Targeting
    target_audience = models.CharField(
        max_length=20,
        choices=TargetAudience.choices,
        default=TargetAudience.ALL
    )

    # Publishing
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin announcement to top of list"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature on homepage"
    )

    # Scheduling
    publish_at = models.DateTimeField(
        default=timezone.now,
        help_text="When to publish the announcement"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When announcement expires (optional)"
    )

    # Authorship and approval
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_announcements'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_announcements'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # Attachments
    attachment = models.FileField(
        upload_to=upload_to_announcements,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])],
        help_text="Optional attachment (PDF, DOC, DOCX, JPG, PNG)"
    )

    # Engagement tracking
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_pinned', '-priority', '-publish_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['announcement_type']),
            models.Index(fields=['target_audience']),
            models.Index(fields=['publish_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['-is_pinned', '-priority']),
        ]
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        return f"{self.title} ({self.get_announcement_type_display()})"

    def save(self, *args, **kwargs):
        # Auto-generate summary if not provided
        if not self.summary and self.content:
            self.summary = self.content[:297] + '...' if len(self.content) > 300 else self.content

        # Set approval timestamp
        if self.status == StatusChoices.APPROVED and not self.approved_at:
            self.approved_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """Check if announcement is currently published"""
        now = timezone.now()
        return (
            self.status == StatusChoices.PUBLISHED and
            self.publish_at <= now and
            (self.expires_at is None or self.expires_at > now)
        )

    @property
    def is_expired(self):
        """Check if announcement has expired"""
        return self.expires_at and self.expires_at <= timezone.now()

    def can_be_viewed_by(self, user):
        """Check if user can view this announcement"""
        if not self.is_published:
            return False

        if self.target_audience == TargetAudience.ALL:
            return True
        elif self.target_audience == TargetAudience.APPROVED_USERS:
            return user.is_authenticated and user.is_approved
        elif self.target_audience == TargetAudience.RESEARCHERS:
            return user.is_authenticated and user.is_researcher
        elif self.target_audience == TargetAudience.MODERATORS:
            return user.is_authenticated and (user.is_moderator or user.is_admin)
        elif self.target_audience == TargetAudience.ADMINS:
            return user.is_authenticated and user.is_admin

        return False

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class AnnouncementImage(TimeStampedModel):
    """
    Model for announcement images
    """
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to=upload_to_announcement_images,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        help_text="Announcement image (JPG, PNG, GIF, WebP)"
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional image caption"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alternative text for accessibility"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (0 = first)"
    )

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Announcement Image'
        verbose_name_plural = 'Announcement Images'

    def __str__(self):
        return f"Image for {self.announcement.title}"


class AnnouncementAttachment(TimeStampedModel):
    """
    Model for announcement file attachments
    """
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(
        upload_to=upload_to_announcements,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'])],
        help_text="Announcement attachment (PDF, DOC, XLS, PPT, TXT)"
    )
    title = models.CharField(
        max_length=200,
        help_text="Display name for the attachment"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the attachment"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times downloaded"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Announcement Attachment'
        verbose_name_plural = 'Announcement Attachments'

    def __str__(self):
        return f"{self.title} - {self.announcement.title}"

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class PostCategory(models.TextChoices):
    """Categories for posts"""
    EVENT = 'event', 'Event'
    ACTIVITY = 'activity', 'Activity'
    WORKSHOP = 'workshop', 'Workshop'
    SEMINAR = 'seminar', 'Seminar'
    CONFERENCE = 'conference', 'Conference'
    TRAINING = 'training', 'Training'
    COLLABORATION = 'collaboration', 'Collaboration'
    ACHIEVEMENT = 'achievement', 'Achievement'
    GENERAL = 'general', 'General'


def upload_to_posts(instance, filename):
    """Upload post attachments to organized directories"""
    return f'content/posts/{instance.id}/{filename}'


class Post(TimeStampedModel):
    """
    Model for events, activities, and general content posts
    """
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Main post content")
    excerpt = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief excerpt for list views (auto-generated if empty)"
    )

    # Classification
    category = models.CharField(
        max_length=20,
        choices=PostCategory.choices,
        default=PostCategory.GENERAL
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags for categorization"
    )

    # Event-specific fields
    event_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time for events (optional)"
    )
    event_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Location for events (optional)"
    )
    registration_required = models.BooleanField(
        default=False,
        help_text="Whether registration is required for this event"
    )
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Registration deadline (if applicable)"
    )
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants (optional)"
    )

    # Publishing
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature on homepage"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Visible to public (non-authenticated users)"
    )

    # Scheduling
    publish_at = models.DateTimeField(
        default=timezone.now,
        help_text="When to publish the post"
    )

    # Authorship and approval
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_posts'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_posts'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # Media attachments
    featured_image = models.ImageField(
        upload_to=upload_to_posts,
        blank=True,
        help_text="Featured image for the post"
    )
    attachment = models.FileField(
        upload_to=upload_to_posts,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])],
        help_text="Optional attachment (PDF, DOC, DOCX, JPG, PNG)"
    )

    # Engagement tracking
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_featured', '-publish_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['publish_at']),
            models.Index(fields=['event_date']),
            models.Index(fields=['-is_featured', '-publish_at']),
        ]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    def save(self, *args, **kwargs):
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = self.content[:297] + '...' if len(self.content) > 300 else self.content

        # Set approval timestamp
        if self.status == StatusChoices.APPROVED and not self.approved_at:
            self.approved_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """Check if post is currently published"""
        return (
            self.status == StatusChoices.PUBLISHED and
            self.publish_at <= timezone.now()
        )

    @property
    def is_event(self):
        """Check if this post is an event"""
        return self.category in [
            PostCategory.EVENT,
            PostCategory.WORKSHOP,
            PostCategory.SEMINAR,
            PostCategory.CONFERENCE,
            PostCategory.TRAINING
        ]

    @property
    def is_upcoming_event(self):
        """Check if this is an upcoming event"""
        return self.is_event and self.event_date and self.event_date > timezone.now()

    @property
    def is_past_event(self):
        """Check if this is a past event"""
        return self.is_event and self.event_date and self.event_date <= timezone.now()

    @property
    def registration_open(self):
        """Check if registration is still open"""
        if not self.registration_required:
            return False

        now = timezone.now()
        if self.registration_deadline and self.registration_deadline <= now:
            return False

        if self.event_date and self.event_date <= now:
            return False

        return True

    @property
    def tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []

    def can_be_viewed_by(self, user):
        """Check if user can view this post"""
        if not self.is_published:
            return False

        if self.is_public:
            return True

        return user.is_authenticated and user.is_approved

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])





class Comment(TimeStampedModel):
    """
    Model for comments on posts and announcements
    """
    # Generic foreign key to allow comments on both posts and announcements
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Comment content
    content = models.TextField(max_length=1000)

    # Authorship
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    # Moderation
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_comments'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # Threading support
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Engagement
    like_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['author']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['parent']),
        ]
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.content_object}"

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None

    def can_be_viewed_by(self, user):
        """Check if user can view this comment"""
        if not self.is_approved:
            return user.is_authenticated and (user == self.author or user.is_admin or user.is_moderator)
        return True


class CommentLike(TimeStampedModel):
    """
    Model for tracking user likes on comments
    """
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )

    class Meta:
        unique_together = ['comment', 'user']
        verbose_name = 'Comment Like'
        verbose_name_plural = 'Comment Likes'

    def __str__(self):
        return f"{self.user.get_full_name()} likes comment by {self.comment.author.get_full_name()}"
