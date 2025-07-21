from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Publication, PublicationAuthor, PublicationMetrics


class PublicationAuthorInline(admin.TabularInline):
    """Inline for managing publication authors"""
    model = PublicationAuthor
    extra = 1
    fields = (
        'author', 'order', 'role', 'is_corresponding',
        'is_first_author', 'is_last_author', 'contribution'
    )
    autocomplete_fields = ['author']
    ordering = ['order']


class PublicationMetricsInline(admin.StackedInline):
    """Inline for publication metrics"""
    model = PublicationMetrics
    can_delete = False
    fields = (
        ('view_count', 'download_count'),
        ('citation_count', 'altmetric_score'),
        ('twitter_mentions', 'facebook_shares', 'linkedin_shares'),
        ('mendeley_readers', 'researchgate_reads'),
        ('last_citation_update', 'last_altmetric_update'),
    )
    readonly_fields = ('last_citation_update', 'last_altmetric_update')


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    """Admin interface for Publication model"""

    list_display = (
        'title_short', 'publication_type', 'status', 'author_count',
        'publication_date', 'submitted_by', 'is_public', 'citation_count'
    )
    list_filter = (
        'status', 'publication_type', 'is_public', 'publication_date',
        'submitted_at', 'research_area'
    )
    search_fields = (
        'title', 'abstract', 'keywords', 'journal_name',
        'conference_name', 'doi', 'authors__first_name',
        'authors__last_name', 'authors__email'
    )
    readonly_fields = (
        'submitted_at', 'created_at', 'updated_at', 'author_names_display'
    )
    autocomplete_fields = ['submitted_by', 'corresponding_author', 'reviewed_by']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'abstract', 'publication_type', 'research_area'
            )
        }),
        ('Publication Details', {
            'fields': (
                ('journal_name', 'conference_name'),
                ('publisher', 'publication_date'),
                ('volume', 'issue', 'pages'),
            )
        }),
        ('Identifiers & Links', {
            'fields': (
                ('doi', 'isbn', 'issn', 'pmid'),
                ('url', 'pdf_url'),
                'document_file',
            )
        }),
        ('Authors & Correspondence', {
            'fields': (
                'corresponding_author', 'author_names_display'
            )
        }),
        ('Content & Keywords', {
            'fields': ('keywords',),
            'classes': ('collapse',)
        }),
        ('Submission & Review', {
            'fields': (
                ('submitted_by', 'submitted_at'),
                ('status', 'is_public'),
                ('reviewed_by', 'reviewed_at'),
                'review_notes',
            )
        }),
        ('Metrics', {
            'fields': ('citation_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [PublicationAuthorInline, PublicationMetricsInline]

    actions = ['approve_publications', 'reject_publications', 'publish_publications']

    def title_short(self, obj):
        """Display shortened title"""
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def author_count(self, obj):
        """Display number of authors"""
        count = obj.authors.count()
        return format_html(
            '<span style="color: {};">{} author{}</span>',
            'green' if count > 0 else 'red',
            count,
            's' if count != 1 else ''
        )
    author_count.short_description = 'Authors'

    def author_names_display(self, obj):
        """Display author names as read-only field"""
        if obj.pk:
            authors = obj.author_assignments.select_related('author').order_by('order')
            author_list = []
            for assignment in authors:
                author_info = assignment.author.get_full_name() or assignment.author.username
                if assignment.is_corresponding:
                    author_info += " (Corresponding)"
                if assignment.is_first_author:
                    author_info += " (First)"
                if assignment.is_last_author:
                    author_info += " (Last)"
                author_list.append(author_info)
            return mark_safe('<br>'.join(author_list)) if author_list else "No authors assigned"
        return "Save publication first to assign authors"
    author_names_display.short_description = 'Current Authors'

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related"""
        return super().get_queryset(request).prefetch_related(
            'authors', 'author_assignments__author'
        ).select_related('submitted_by', 'corresponding_author', 'reviewed_by')

    def approve_publications(self, request, queryset):
        """Bulk approve publications"""
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} publications approved.')
    approve_publications.short_description = 'Approve selected publications'

    def reject_publications(self, request, queryset):
        """Bulk reject publications"""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} publications rejected.')
    reject_publications.short_description = 'Reject selected publications'

    def publish_publications(self, request, queryset):
        """Bulk publish approved publications"""
        updated = queryset.filter(status='approved').update(
            status='published',
            is_public=True
        )
        self.message_user(request, f'{updated} publications published.')
    publish_publications.short_description = 'Publish selected approved publications'


@admin.register(PublicationAuthor)
class PublicationAuthorAdmin(admin.ModelAdmin):
    """Admin interface for PublicationAuthor model"""

    list_display = (
        'publication_title', 'author_name', 'order', 'role',
        'is_corresponding', 'is_first_author', 'is_last_author'
    )
    list_filter = (
        'is_corresponding', 'is_first_author', 'is_last_author',
        'publication__status', 'publication__publication_type'
    )
    search_fields = (
        'publication__title', 'author__first_name', 'author__last_name',
        'author__email', 'role', 'affiliation_at_publication'
    )
    autocomplete_fields = ['publication', 'author']

    fieldsets = (
        ('Assignment', {
            'fields': ('publication', 'author', 'order')
        }),
        ('Role & Contribution', {
            'fields': ('role', 'contribution', 'affiliation_at_publication')
        }),
        ('Author Flags', {
            'fields': (
                'is_corresponding', 'is_first_author', 'is_last_author'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def publication_title(self, obj):
        """Display publication title"""
        title = obj.publication.title
        return title[:40] + "..." if len(title) > 40 else title
    publication_title.short_description = 'Publication'

    def author_name(self, obj):
        """Display author name"""
        return obj.author.get_full_name() or obj.author.username
    author_name.short_description = 'Author'

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'publication', 'author'
        )


@admin.register(PublicationMetrics)
class PublicationMetricsAdmin(admin.ModelAdmin):
    """Admin interface for PublicationMetrics model"""

    list_display = (
        'publication_title', 'view_count', 'download_count',
        'citation_count', 'total_engagement_score', 'updated_at'
    )
    list_filter = ('last_citation_update', 'last_altmetric_update', 'updated_at')
    search_fields = ('publication__title', 'publication__authors__first_name', 'publication__authors__last_name')
    readonly_fields = ('created_at', 'updated_at', 'total_engagement_score')
    autocomplete_fields = ['publication']

    fieldsets = (
        ('Publication', {
            'fields': ('publication',)
        }),
        ('View & Download Metrics', {
            'fields': ('view_count', 'download_count')
        }),
        ('Citation & Academic Metrics', {
            'fields': (
                ('citation_count', 'altmetric_score'),
                ('mendeley_readers', 'researchgate_reads'),
                ('last_citation_update', 'last_altmetric_update')
            )
        }),
        ('Social Media Metrics', {
            'fields': (
                'twitter_mentions', 'facebook_shares', 'linkedin_shares'
            ),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('total_engagement_score',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def publication_title(self, obj):
        """Display publication title"""
        title = obj.publication.title
        return title[:40] + "..." if len(title) > 40 else title
    publication_title.short_description = 'Publication'

    def total_engagement_score(self, obj):
        """Display total engagement score"""
        score = obj.total_engagement
        return format_html(
            '<span style="font-weight: bold; color: {};">{}</span>',
            'green' if score > 100 else 'orange' if score > 50 else 'red',
            score
        )
    total_engagement_score.short_description = 'Engagement Score'

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('publication')
