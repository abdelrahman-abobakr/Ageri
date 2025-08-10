from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
import csv
from datetime import datetime

from .models import (
    Publication, PublicationAuthor, PublicationMetrics
)
from .forms import PublicationAdminForm, BulkActionForm

# Custom filters
class PublicationStatusFilter(SimpleListFilter):
    title = 'Publication Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('published', 'Published'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(status='pending')
        elif self.value() == 'approved':
            return queryset.filter(status='approved')
        elif self.value() == 'rejected':
            return queryset.filter(status='rejected')
        elif self.value() == 'published':
            return queryset.filter(status='published')

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    form = PublicationAdminForm
    list_display = ['title', 'publication_type', 'status', 'journal_name', 'publication_date', 'created_at']
    list_filter = [PublicationStatusFilter, 'publication_type', 'created_at']
    search_fields = ['title', 'abstract', 'journal_name', 'doi']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'abstract', 'publication_type', 'status')
        }),
        ('Publication Details', {
            'fields': ('journal_name', 'conference_name', 'publisher', 'volume', 'issue', 'pages', 'doi', 'isbn')
        }),
        ('Dates', {
            'fields': ('submitted_at', 'publication_date')
        }),
        ('Additional Info', {
            'fields': ('keywords', 'research_area', 'document_file'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(PublicationAuthor)
class PublicationAuthorAdmin(admin.ModelAdmin):
    list_display = ['publication', 'author', 'order', 'is_corresponding']
    list_filter = ['is_corresponding', 'order']
    search_fields = ['publication__title', 'author__username', 'author__email']

@admin.register(PublicationMetrics)
class PublicationMetricsAdmin(admin.ModelAdmin):
    list_display = ['publication', 'citation_count', 'view_count', 'download_count', 'updated_at']
    readonly_fields = ['updated_at']
    search_fields = ['publication__title']



# Enhanced admin site customization
admin.site.site_header = "Research Publications Admin"
admin.site.site_title = "Publications Admin"
admin.site.index_title = "Publications Management"

# Add custom CSS and JS
class PublicationAdminSite(admin.AdminSite):
    """Custom admin site with enhanced features"""
    
    def each_context(self, request):
        """Add custom context to all admin pages"""
        context = super().each_context(request)
        context.update({
            'custom_css': 'admin/css/publications.css',
            'custom_js': 'admin/js/publications.js',
        })
        return context
