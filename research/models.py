from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from core.models import TimeStampedModel, StatusChoices, upload_to_documents


class PublicationType(models.TextChoices):
    """Publication type choices"""
    JOURNAL_ARTICLE = 'journal_article', 'Journal Article'
    CONFERENCE_PAPER = 'conference_paper', 'Conference Paper'
    BOOK_CHAPTER = 'book_chapter', 'Book Chapter'
    BOOK = 'book', 'Book'
    THESIS = 'thesis', 'Thesis'
    REPORT = 'report', 'Report'
    PREPRINT = 'preprint', 'Preprint'
    OTHER = 'other', 'Other'


def upload_to_publications(instance, filename):
    """
    Upload publication files to organized directories
    """
    return f'publications/{instance.id}/{filename}'


class Publication(TimeStampedModel):
    """
    Publication model for research papers and documents
    """
    # Basic Information
    title = models.CharField(max_length=500)
    abstract = models.TextField(blank=True, max_length=2000)
    publication_type = models.CharField(
        max_length=20,
        choices=PublicationType.choices,
        default=PublicationType.JOURNAL_ARTICLE
    )

    # Authors (Many-to-Many relationship with User)
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PublicationAuthor',
        related_name='publications',
        help_text="Researchers who authored this publication"
    )

    # Corresponding Author
    corresponding_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corresponding_publications',
        help_text="Main contact author for this publication"
    )

    # Publication Details
    journal_name = models.CharField(max_length=300, blank=True)
    conference_name = models.CharField(max_length=300, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=50, blank=True, help_text="e.g., 123-145")
    publication_date = models.DateField(null=True, blank=True)

    # Identifiers
    doi = models.CharField(max_length=200, blank=True, help_text="Digital Object Identifier")
    isbn = models.CharField(max_length=20, blank=True, help_text="International Standard Book Number")
    issn = models.CharField(max_length=20, blank=True, help_text="International Standard Serial Number")
    pmid = models.CharField(max_length=20, blank=True, help_text="PubMed ID")

    # URLs and Links
    url = models.URLField(blank=True, help_text="Link to publication")
    pdf_url = models.URLField(blank=True, help_text="Direct link to PDF")

    # File Upload
    document_file = models.FileField(
        upload_to=upload_to_publications,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text="Upload publication document (PDF, DOC, DOCX only)"
    )

    # Keywords and Categories
    keywords = models.TextField(
        blank=True,
        help_text="Comma-separated keywords"
    )
    research_area = models.CharField(max_length=200, blank=True)

    # Approval Workflow
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_publications',
        help_text="User who submitted this publication"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Admin Review
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_publications',
        help_text="Admin who reviewed this publication"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Admin notes about the review")

    # Visibility
    is_public = models.BooleanField(
        default=False,
        help_text="Make publication visible to public"
    )

    # Citation Count (can be updated manually or via API)
    citation_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        ordering = ['-publication_date', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['publication_type']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"{self.title[:50]}..." if len(self.title) > 50 else self.title

    @property
    def author_names(self):
        """Get comma-separated list of author names"""
        return ", ".join([
            author.get_full_name() or author.username
            for author in self.authors.all()
        ])

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

    def get_absolute_url(self):
        """Get URL for publication detail view"""
        return reverse('research:publication-detail', kwargs={'pk': self.pk})

    def can_be_edited_by(self, user):
        """Check if user can edit this publication"""
        if user.is_admin:
            return True
        if self.status == StatusChoices.DRAFT:
            return user == self.submitted_by or user in self.authors.all()
        return False

    def can_be_approved_by(self, user):
        """Check if user can approve this publication"""
        return user.is_admin and self.status == StatusChoices.PENDING


class PublicationAuthor(TimeStampedModel):
    """
    Through model for Publication-Author relationship with additional metadata
    """
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='author_assignments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publication_assignments'
    )

    # Author order and role
    order = models.PositiveIntegerField(
        default=1,
        help_text="Order of author in publication (1 = first author)"
    )
    role = models.CharField(
        max_length=100,
        blank=True,
        help_text="Author's role in the research (e.g., Principal Investigator, Data Analyst)"
    )

    # Affiliation at time of publication
    affiliation_at_publication = models.CharField(
        max_length=300,
        blank=True,
        help_text="Author's affiliation when this publication was created"
    )

    # Contribution details
    contribution = models.TextField(
        blank=True,
        help_text="Description of author's contribution to the research"
    )

    # Flags
    is_corresponding = models.BooleanField(
        default=False,
        help_text="Is this author the corresponding author?"
    )
    is_first_author = models.BooleanField(
        default=False,
        help_text="Is this the first author?"
    )
    is_last_author = models.BooleanField(
        default=False,
        help_text="Is this the last/senior author?"
    )

    class Meta:
        verbose_name = 'Publication Author'
        verbose_name_plural = 'Publication Authors'
        ordering = ['publication', 'order']
        unique_together = ['publication', 'author']
        indexes = [
            models.Index(fields=['publication', 'order']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"{self.author.get_full_name()} - {self.publication.title[:30]}..."

    def save(self, *args, **kwargs):
        """Override save to set affiliation if not provided"""
        if not self.affiliation_at_publication and hasattr(self.author, 'institution'):
            self.affiliation_at_publication = self.author.institution
        super().save(*args, **kwargs)


class PublicationMetrics(TimeStampedModel):
    """
    Model to track publication metrics and analytics
    """
    publication = models.OneToOneField(
        Publication,
        on_delete=models.CASCADE,
        related_name='metrics'
    )

    # View and Download Counts
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    # External Metrics (can be updated via APIs)
    citation_count = models.PositiveIntegerField(default=0)
    altmetric_score = models.FloatField(null=True, blank=True)

    # Social Media Metrics
    twitter_mentions = models.PositiveIntegerField(default=0)
    facebook_shares = models.PositiveIntegerField(default=0)
    linkedin_shares = models.PositiveIntegerField(default=0)

    # Academic Metrics
    mendeley_readers = models.PositiveIntegerField(default=0)
    researchgate_reads = models.PositiveIntegerField(default=0)

    # Last updated timestamps
    last_citation_update = models.DateTimeField(null=True, blank=True)
    last_altmetric_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Publication Metrics'
        verbose_name_plural = 'Publication Metrics'

    def __str__(self):
        return f"Metrics for {self.publication.title[:30]}..."

    @property
    def total_engagement(self):
        """Calculate total engagement score"""
        return (
            self.view_count +
            self.download_count * 2 +
            self.citation_count * 5 +
            self.twitter_mentions +
            self.facebook_shares +
            self.linkedin_shares
        )
