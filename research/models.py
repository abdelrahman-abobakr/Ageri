from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
from django.contrib.auth import get_user_model

User = get_user_model()

# Import from core.models if available, otherwise define locally
try:
    from core.models import TimeStampedModel, StatusChoices, upload_to_documents
except ImportError:
    # Define locally if core.models doesn't exist
    class TimeStampedModel(models.Model):
        """Abstract base class with timestamp fields"""
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        
        class Meta:
            abstract = True

    class StatusChoices(models.TextChoices):
        """Status choices for publications"""
        DRAFT = 'draft', _('Draft')
        PENDING = 'pending', _('Pending Review')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        PUBLISHED = 'published', _('Published')

    def upload_to_documents(instance, filename):
        """Generic upload function"""
        return f'documents/{instance.id}/{filename}'


class PublicationType(models.TextChoices):
    """Publication type choices"""
    JOURNAL_ARTICLE = 'journal_article', _('Journal Article')
    CONFERENCE_PAPER = 'conference_paper', _('Conference Paper')
    BOOK_CHAPTER = 'book_chapter', _('Book Chapter')
    BOOK = 'book', _('Book')
    THESIS = 'thesis', _('Thesis')
    REPORT = 'report', _('Report')
    PREPRINT = 'preprint', _('Preprint')
    OTHER = 'other', _('Other')


def upload_to_publications(instance, filename):
    """
    Upload publication files to organized directories
    """
    # Sanitize filename
    name, ext = os.path.splitext(filename)
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_name[:50]}{ext}"  # Limit filename length
    
    return f'publications/{instance.id}/{filename}'


class PublicationQuerySet(models.QuerySet):
    """Custom QuerySet for Publication model"""
    
    def published(self):
        """Filter published publications"""
        return self.filter(status=StatusChoices.PUBLISHED, is_public=True)
    
    def pending_review(self):
        """Filter publications pending review"""
        return self.filter(status=StatusChoices.PENDING)
    
    def by_type(self, publication_type):
        """Filter by publication type"""
        return self.filter(publication_type=publication_type)
    
    def with_authors(self):
        """Prefetch authors for optimization"""
        return self.prefetch_related(
            'author_assignments__author',
            'authors'
        ).select_related('corresponding_author', 'submitted_by')
    
    def with_metrics(self):
        """Include metrics in query"""
        return self.select_related('metrics')
    
    def recent(self, days=30):
        """Filter recent publications"""
        from django.utils import timezone
        return self.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=days)
        )


class PublicationManager(models.Manager):
    """Custom Manager for Publication model"""
    
    def get_queryset(self):
        return PublicationQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def pending_review(self):
        return self.get_queryset().pending_review()
    
    def by_type(self, publication_type):
        return self.get_queryset().by_type(publication_type)
    
    def recent(self, days=30):
        return self.get_queryset().recent(days)


class Publication(TimeStampedModel):
    """
    Enhanced Publication model for research papers and documents
    """
    # Basic Information
    title = models.CharField(
        max_length=500,
        blank=True,  # Allow blank in forms
        null=True,   # Allow NULL in database
        help_text=_("Publication title")
    )
    abstract = models.TextField(
        blank=True,
        max_length=2000,
        help_text=_("Publication abstract")
    )
    publication_type = models.CharField(
        max_length=20,
        choices=PublicationType.choices,
        default=PublicationType.JOURNAL_ARTICLE,
        db_index=True
    )

    # Authors (Many-to-Many relationship with User)
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PublicationAuthor',
        related_name='publications',
        help_text=_("Researchers who authored this publication")
    )

    # Corresponding Author
    corresponding_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corresponding_publications',
        help_text=_("Main contact author for this publication")
    )

    # Publication Details
    journal_name = models.CharField(
        max_length=300,
        blank=True,
        help_text=_("Journal name")
    )
    conference_name = models.CharField(
        max_length=300,
        blank=True,
        help_text=_("Conference name")
    )
    publisher = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Publisher name")
    )
    volume = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Volume number")
    )
    issue = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Issue number")
    )
    pages = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Page range (e.g., 123-145)")
    )
    publication_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Date of publication")
    )

    # Identifiers with validation
    doi = models.CharField(
        max_length=200,
        blank=True,
        unique=True,
        null=True,
        help_text=_("Digital Object Identifier (must start with 10.)")
    )
    isbn = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("International Standard Book Number")
    )
    issn = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("International Standard Serial Number")
    )
    pmid = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("PubMed ID")
    )

    # URLs and Links
    url = models.URLField(
        blank=True,
        help_text=_("Link to publication")
    )
    pdf_url = models.URLField(
        blank=True,
        help_text=_("Direct link to PDF")
    )

    # File Upload with enhanced validation
    document_file = models.FileField(
        upload_to=upload_to_publications,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text=_("Upload publication document (PDF, DOC, DOCX only, max 10MB)")
    )

    # Keywords and Categories
    keywords = models.TextField(
        blank=True,
        help_text=_("Comma-separated keywords")
    )
    research_area = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        help_text=_("Research area/field")
    )

    # Approval Workflow
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        db_index=True
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_publications',
        help_text=_("User who submitted this publication")
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    # Admin Review
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_publications',
        help_text=_("Admin who reviewed this publication")
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(
        blank=True,
        help_text=_("Admin notes about the review")
    )

    # Visibility
    is_public = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Make publication visible to public")
    )

    # Citation Count with validation
    citation_count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )

    # Priority and Featured flags
    is_featured = models.BooleanField(
        default=False,
        help_text=_("Feature this publication")
    )
    priority = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text=_("Priority for ordering (0-10)")
    )

    objects = PublicationManager()

    class Meta:
        verbose_name = _('Publication')
        verbose_name_plural = _('Publications')
        ordering = ['-priority', '-publication_date', '-created_at']
        indexes = [
            models.Index(fields=['status', 'is_public']),
            models.Index(fields=['publication_type']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['research_area']),
            models.Index(fields=['is_featured', 'priority']),
            models.Index(fields=['corresponding_author']),
            models.Index(fields=['submitted_by']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(priority__gte=0) & models.Q(priority__lte=10),
                name='valid_priority_range'
            ),
        ]

    def __str__(self):
        return self.title[:50] + "..." if len(self.title) > 50 else self.title

    def clean(self):
        """Model validation"""
        super().clean()
        
        # Validate DOI format
        if self.doi and not self.doi.startswith('10.'):
            raise ValidationError({'doi': _('DOI must start with "10."')})
        
        # Validate publication date
        if self.publication_date:
            from django.utils import timezone
            if self.publication_date > timezone.now().date():
                raise ValidationError({
                    'publication_date': _('Publication date cannot be in the future')
                })
        
        # Validate file size (10MB limit)
        if self.document_file and self.document_file.size > 10 * 1024 * 1024:
            raise ValidationError({
                'document_file': _('File size cannot exceed 10MB')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def author_names(self):
        """Get comma-separated list of author names"""
        return ", ".join([
            author.get_full_name() or author.username
            for author in self.authors.all()
        ])

    @property
    def first_authors(self):
        """Get first authors"""
        return self.author_assignments.filter(is_first_author=True).select_related('author')

    @property
    def corresponding_authors(self):
        """Get corresponding authors"""
        return self.author_assignments.filter(is_corresponding=True).select_related('author')

    @property
    def is_pending_review(self):
        """Check if publication is pending admin review"""
        return self.status == StatusChoices.PENDING

    @property
    def is_approved(self):
        """Check if publication is approved"""
        return self.status == StatusChoices.APPROVED

    @property
    def is_published(self):
        """Check if publication is published and public"""
        return self.status == StatusChoices.PUBLISHED and self.is_public

    @property
    def is_draft(self):
        """Check if publication is in draft status"""
        return self.status == StatusChoices.DRAFT

    @property
    def total_views(self):
        """Get total view count from metrics"""
        return getattr(self.metrics, 'view_count', 0) if hasattr(self, 'metrics') else 0

    @property
    def total_downloads(self):
        """Get total download count from metrics"""
        return getattr(self.metrics, 'download_count', 0) if hasattr(self, 'metrics') else 0

    def get_absolute_url(self):
        """Get URL for publication detail view"""
        return reverse('research:publication-detail', kwargs={'pk': self.pk})

    def can_be_edited_by(self, user):
        """Check if user can edit this publication"""
        if not user or not user.is_authenticated:
            return False
        if hasattr(user, 'is_admin') and user.is_admin:
            return True
        if self.status == StatusChoices.DRAFT:
            return user == self.submitted_by or user in self.authors.all()
        return False

    def can_be_approved_by(self, user):
        """Check if user can approve this publication"""
        if not user or not user.is_authenticated:
            return False
        return (hasattr(user, 'is_admin') and user.is_admin and 
                self.status == StatusChoices.PENDING)

    def can_be_viewed_by(self, user):
        """Check if user can view this publication"""
        if self.is_published:
            return True
        if not user or not user.is_authenticated:
            return False
        if hasattr(user, 'is_admin') and user.is_admin:
            return True
        return user == self.submitted_by or user in self.authors.all()


class PublicationAuthor(models.Model):
    """Enhanced through model for Publication-Author relationship"""
    
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='author_assignments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='publication_authorships'
    )
    
    # Author details
    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_("Order of author in publication (1 = first author)")
    )
    role = models.CharField(
        max_length=100, 
        blank=True,
        help_text=_("Author's role in the research")
    )
    affiliation_at_publication = models.CharField(
        max_length=300, 
        blank=True,
        help_text=_("Author's affiliation when this publication was created")
    )
    contribution = models.TextField(
        blank=True,
        help_text=_("Description of author's contribution to the research")
    )
    
    # Author flags with enhanced constraints
    is_corresponding = models.BooleanField(
        default=False,
        help_text=_("Is this author the corresponding author?")
    )
    is_first_author = models.BooleanField(
        default=False,
        help_text=_("Is this the first author?")
    )
    is_last_author = models.BooleanField(
        default=False,
        help_text=_("Is this the last/senior author?")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Publication Author')
        verbose_name_plural = _('Publication Authors')
        unique_together = ['publication', 'author']
        ordering = ['publication', 'order']
        indexes = [
            models.Index(fields=['publication', 'order']),
            models.Index(fields=['author']),
            models.Index(fields=['is_corresponding']),
            models.Index(fields=['is_first_author', 'is_last_author']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(order__gte=1) & models.Q(order__lte=100),
                name='valid_author_order'
            ),
        ]
    
    def __str__(self):
        author_name = self.author.get_full_name() or self.author.username
        return f"{author_name} - {self.publication.title[:30]}..."
    
    def clean(self):
        """Enhanced model validation"""
        super().clean()
        
        # Validate that first author has order = 1 if set
        if self.is_first_author and self.order != 1:
            raise ValidationError({
                'order': _('First author must have order = 1')
            })
    
    def save(self, *args, **kwargs):
        """Override save to set affiliation and validate"""
        if not self.affiliation_at_publication and hasattr(self.author, 'institution'):
            self.affiliation_at_publication = getattr(self.author, 'institution', '')
        
        self.full_clean()
        super().save(*args, **kwargs)


class PublicationMetrics(models.Model):
    """Enhanced model for tracking publication metrics"""
    
    publication = models.OneToOneField(
        Publication,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # View and download metrics
    view_count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    download_count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # External metrics
    citation_count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    altmetric_score = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Altmetric attention score")
    )
    
    # Social media metrics
    twitter_mentions = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    facebook_shares = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    linkedin_shares = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Academic metrics
    mendeley_readers = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    researchgate_reads = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Last updated timestamps
    last_citation_update = models.DateTimeField(null=True, blank=True)
    last_altmetric_update = models.DateTimeField(null=True, blank=True)
    
    # Quality scores
    quality_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text=_("Quality score (0-10)")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Publication Metrics')
        verbose_name_plural = _('Publication Metrics')
        ordering = ['-citation_count', '-view_count']
        indexes = [
            models.Index(fields=['view_count']),
            models.Index(fields=['download_count']),
            models.Index(fields=['citation_count']),
            models.Index(fields=['quality_score']),
        ]
    
    def __str__(self):
        return f"Metrics for {self.publication.title[:50]}..."
    
    @property
    def total_engagement(self):
        """Calculate enhanced total engagement score"""
        social_score = (
            self.twitter_mentions +
            self.facebook_shares +
            self.linkedin_shares
        )
        
        academic_score = (
            self.mendeley_readers +
            self.researchgate_reads
        )
        
        return (
            self.view_count +
            self.download_count * 2 +
            self.citation_count * 5 +
            social_score +
            academic_score * 1.5
        )
    
    @property
    def engagement_level(self):
        """Get engagement level description"""
        score = self.total_engagement
        if score >= 1000:
            return 'Very High'
        elif score >= 500:
            return 'High'
        elif score >= 100:
            return 'Medium'
        elif score >= 10:
            return 'Low'
        else:
            return 'Very Low'
    
    def calculate_quality_score(self):
        """Calculate quality score based on various metrics"""
        # Base score from engagement
        engagement_factor = min(self.total_engagement / 1000, 5.0)
        
        # Citation factor
        citation_factor = min(self.citation_count / 10, 3.0)
        
        # Social media factor
        social_factor = min((self.twitter_mentions + self.facebook_shares) / 50, 2.0)
        
        # Calculate final score
        self.quality_score = min(engagement_factor + citation_factor + social_factor, 10.0)
        return self.quality_score
    
    def save(self, *args, **kwargs):
        """Override save to calculate quality score"""
        self.calculate_quality_score()
        super().save(*args, **kwargs)
