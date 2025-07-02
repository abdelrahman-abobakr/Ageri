from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Announcement, Post, Comment, CommentLike


class CommentInline(GenericTabularInline):
    """Inline for comments on posts and announcements"""
    model = Comment
    extra = 0
    fields = ['author', 'content', 'is_approved', 'created_at']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Admin interface for announcements"""
    list_display = [
        'title_short', 'announcement_type', 'priority', 'target_audience',
        'status', 'is_pinned', 'is_featured', 'author', 'publish_at', 'view_count'
    ]
    list_filter = [
        'announcement_type', 'priority', 'target_audience', 'status',
        'is_pinned', 'is_featured', 'created_at', 'publish_at'
    ]
    search_fields = ['title', 'content', 'summary']
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'approved_at']
    date_hierarchy = 'publish_at'
    ordering = ['-is_pinned', '-priority', '-publish_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'summary')
        }),
        ('Classification', {
            'fields': ('announcement_type', 'priority', 'target_audience')
        }),
        ('Publishing', {
            'fields': ('status', 'is_pinned', 'is_featured', 'publish_at', 'expires_at')
        }),
        ('Authorship', {
            'fields': ('author', 'approved_by', 'approved_at')
        }),
        ('Attachments', {
            'fields': ('attachment',)
        }),
        ('Metrics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [CommentInline]

    actions = ['approve_announcements', 'publish_announcements', 'pin_announcements', 'unpin_announcements']

    def title_short(self, obj):
        """Display shortened title"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def approve_announcements(self, request, queryset):
        """Bulk approve announcements"""
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} announcements approved.')
    approve_announcements.short_description = 'Approve selected announcements'

    def publish_announcements(self, request, queryset):
        """Bulk publish announcements"""
        updated = queryset.filter(status='approved').update(status='published')
        self.message_user(request, f'{updated} announcements published.')
    publish_announcements.short_description = 'Publish selected announcements'

    def pin_announcements(self, request, queryset):
        """Bulk pin announcements"""
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} announcements pinned.')
    pin_announcements.short_description = 'Pin selected announcements'

    def unpin_announcements(self, request, queryset):
        """Bulk unpin announcements"""
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} announcements unpinned.')
    unpin_announcements.short_description = 'Unpin selected announcements'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'approved_by')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for posts"""
    list_display = [
        'title_short', 'category', 'status', 'is_featured', 'is_public',
        'author', 'event_date', 'publish_at', 'view_count'
    ]
    list_filter = [
        'category', 'status', 'is_featured', 'is_public',
        'registration_required', 'created_at', 'publish_at', 'event_date'
    ]
    search_fields = ['title', 'content', 'excerpt', 'tags', 'event_location']
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'approved_at']
    date_hierarchy = 'publish_at'
    ordering = ['-is_featured', '-publish_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'excerpt', 'category', 'tags')
        }),
        ('Event Details', {
            'fields': (
                'event_date', 'event_location', 'registration_required',
                'registration_deadline', 'max_participants'
            ),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'is_public', 'publish_at')
        }),
        ('Authorship', {
            'fields': ('author', 'approved_by', 'approved_at')
        }),
        ('Media', {
            'fields': ('featured_image', 'attachment')
        }),
        ('Metrics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [CommentInline]

    actions = ['approve_posts', 'publish_posts', 'feature_posts', 'unfeature_posts']

    def title_short(self, obj):
        """Display shortened title"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def approve_posts(self, request, queryset):
        """Bulk approve posts"""
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} posts approved.')
    approve_posts.short_description = 'Approve selected posts'

    def publish_posts(self, request, queryset):
        """Bulk publish posts"""
        updated = queryset.filter(status='approved').update(status='published')
        self.message_user(request, f'{updated} posts published.')
    publish_posts.short_description = 'Publish selected posts'

    def feature_posts(self, request, queryset):
        """Bulk feature posts"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts featured.')
    feature_posts.short_description = 'Feature selected posts'

    def unfeature_posts(self, request, queryset):
        """Bulk unfeature posts"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} posts unfeatured.')
    unfeature_posts.short_description = 'Unfeature selected posts'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'approved_by')


class CommentReplyInline(admin.TabularInline):
    """Inline for comment replies"""
    model = Comment
    fk_name = 'parent'
    extra = 0
    fields = ['author', 'content', 'is_approved', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for comments"""
    list_display = [
        'content_short', 'author', 'content_object_link', 'is_approved',
        'is_reply', 'like_count', 'created_at'
    ]
    list_filter = [
        'is_approved', 'content_type', 'created_at'
    ]
    search_fields = ['content', 'author__first_name', 'author__last_name', 'author__email']
    readonly_fields = ['like_count', 'created_at', 'updated_at', 'approved_at', 'content_object']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Comment Information', {
            'fields': ('content', 'author', 'content_object')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
        ('Threading', {
            'fields': ('parent',)
        }),
        ('Metrics', {
            'fields': ('like_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [CommentReplyInline]

    actions = ['approve_comments', 'reject_comments']

    def content_short(self, obj):
        """Display shortened content"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_short.short_description = 'Content'

    def content_object_link(self, obj):
        """Display link to the content object"""
        if obj.content_object:
            if hasattr(obj.content_object, 'title'):
                return format_html(
                    '<a href="{}">{}</a>',
                    reverse(f'admin:{obj.content_type.app_label}_{obj.content_type.model}_change',
                           args=[obj.object_id]),
                    obj.content_object.title[:50]
                )
        return 'N/A'
    content_object_link.short_description = 'Content Object'

    def is_reply(self, obj):
        """Check if comment is a reply"""
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'

    def approve_comments(self, request, queryset):
        """Bulk approve comments"""
        updated = queryset.filter(is_approved=False).update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'

    def reject_comments(self, request, queryset):
        """Bulk reject comments"""
        updated = queryset.filter(is_approved=True).update(
            is_approved=False,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} comments rejected.')
    reject_comments.short_description = 'Reject selected comments'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'author', 'approved_by', 'content_type', 'parent'
        ).prefetch_related('content_object')




@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Admin interface for comment likes"""
    list_display = ['user', 'comment_content', 'comment_author', 'created_at']
    list_filter = ['created_at']
    search_fields = [
        'user__first_name', 'user__last_name', 'user__email',
        'comment__content', 'comment__author__first_name', 'comment__author__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def comment_content(self, obj):
        """Display comment content"""
        return obj.comment.content[:50] + '...' if len(obj.comment.content) > 50 else obj.comment.content
    comment_content.short_description = 'Comment'

    def comment_author(self, obj):
        """Display comment author"""
        return obj.comment.author.get_full_name()
    comment_author.short_description = 'Comment Author'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'comment__author')
